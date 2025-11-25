import asyncio
import configparser
import importlib
import os
import ssl
import sys
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Dict, List, Optional

import aiohttp
from aiohttp.abc import AbstractCookieJar

from pyshowdown import connection, message

if TYPE_CHECKING:
    from pyshowdown.plugins.plugin import BasePlugin
    from pyshowdown.room import Room


THROTTLE = 0.6


class Client:
    def __init__(
        self,
        username: str,
        password: str,
        url: str,
        login_type: str = "password",
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """Client class constructor.

        Args:
            username (str): The username to use.
            password (str): The password to use.
            url (str): The url to connect to.
            login_type (str): The type of login to use. Either "password" or "oauth".
            ssl_context (ssl.SSLContext, optional): The SSL context. Defaults to None.
        """
        self.conn = connection.Connection(url, ssl_context=ssl_context)
        self.username = username
        self.password = password
        self.login_type = login_type
        self.connected = False
        self.cookies: Optional[AbstractCookieJar] = None
        self.plugins: List["BasePlugin"] = []
        self.rooms: Dict[str, "Room"] = {}
        self.logging_in: bool = False
        self.backoff: int = 1
        self._setup_plugin_paths()
        self._load_system_plugins()

    def _setup_plugin_paths(self) -> None:
        """Set up sys.path to include the system plugins directory."""
        system_plugins_path = os.path.join(os.path.dirname(__file__), "plugins")
        if system_plugins_path not in sys.path:
            sys.path.append(system_plugins_path)

    def _load_system_plugins(self) -> None:
        """Load the default system plugins required for basic functionality."""
        system_plugins = ["challstr", "init", "deinit", "title", "users"]
        for plugin_name in system_plugins:
            self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a single plugin by name.

        The plugin module must export a setup(client) function that returns
        a list of BasePlugin instances.

        Args:
            plugin_name (str): The name of the plugin module to load.

        Returns:
            bool: True if plugin loaded successfully, False otherwise.
        """
        try:
            plugin_module = importlib.import_module(plugin_name)
            plugins = plugin_module.setup(self)
            for plugin in plugins:
                self.plugins.append(plugin)
            self.print(f"Successfully loaded plugin: {plugin_name}")
            return True
        except Exception as e:
            self.print(f"Error loading plugin {plugin_name}: {e}")
            return False

    async def connect(self) -> None:
        """Connect to the server."""
        self.print("connecting...")
        await self.conn.connect()

    async def keep_connected(self) -> None:
        """Keeps the client connected to the server."""
        self.connected = False
        self.backoff = 1
        # Keep a reference to the message-queue consumer task so callers
        # can cancel it explicitly during shutdown.
        self._message_queue_task = asyncio.create_task(self.start_message_queue())
        while not self.connected:
            try:
                await asyncio.sleep(self.backoff)
                await self.connect()
                self.connected = True
                await self.receive_forever()
            except Exception as e:
                self.print(e)
            self.backoff *= 2

    async def close(self) -> None:
        """Close the connection."""
        # Cancel the message-queue task if it exists so it won't attempt
        # to use the event loop while it's shutting down.
        task = getattr(self, "_message_queue_task", None)
        if task is not None and not task.done():
            try:
                task.cancel()
            except Exception:
                pass
            try:
                await asyncio.gather(task, return_exceptions=True)
            except Exception:
                # ignore failures while cancelling
                pass

        await self.conn.close()

    async def start_message_queue(self) -> None:
        """Starts the message queue."""
        # Create the queue used for outgoing messages. The consumer will
        # handle cancellation and loop-closed situations so that shutdown
        # can proceed without background tasks scheduling callbacks on a
        # closed loop.
        self.queue = asyncio.Queue()
        try:
            while True:
                try:
                    m = await self.queue.get()
                except asyncio.CancelledError:
                    # Consumer was cancelled, exit cleanly.
                    break
                except RuntimeError:
                    # Event loop is likely closed, stop the consumer.
                    break

                # If the loop is closing, avoid scheduling work.
                try:
                    self.print(">> " + m)
                    await self.conn.send(m)
                except asyncio.CancelledError:
                    break
                except RuntimeError:
                    # Underlying event loop closed while sending.
                    break

                try:
                    await asyncio.sleep(THROTTLE)
                except asyncio.CancelledError:
                    break
        finally:
            # Best-effort cleanup: if queue still exists, drain it to
            # avoid leaving producers blocked on put().
            try:
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                    except Exception:
                        break
            except Exception:
                pass

    async def send(self, room: str, message: str) -> None:
        """Sends message to the server.

        Args:
            message (str): The message to send.
        """
        m = f"{room}|{message}"
        # If the queue hasn't been created yet (not connected), try to
        # create it or raise a clear error. This avoids scheduling put()
        # on a nonexistent/closed loop.
        if not hasattr(self, "queue") or self.queue is None:
            # Create a local queue so callers won't error if the consumer
            # hasn't started yet. The keep_connected logic normally starts
            # the consumer before connecting, so this is defensive.
            self.queue = asyncio.Queue()

        try:
            await self.queue.put(m)
        except RuntimeError:
            # Event loop is closed; ignore the send request.
            return

    async def send_pm(self, user: str, message: str) -> None:
        """Sends a private message to the user.

        Args:
            user (str): The user to send the message to.
            message (str): The message to send.
        """
        await self.send("", f"/w {user}, {message}")

    async def receive(self) -> aiohttp.WSMessage:
        """Receives data from the server.

        Returns:
            aiohttp.WSMessage: The data received.
        """
        return await self.conn.receive()

    async def receive_forever(self) -> None:
        """Receives data from the server forever.

        Raises:
            ConnectionError: If no connection is established.
        """
        if self.conn.ws is None:
            raise ConnectionError("Not connected to server.")
        try:
            async for ws_message in self.conn.ws:
                if ws_message.type == aiohttp.WSMsgType.TEXT:
                    message: str = ws_message.data
                    if message:
                        # some messages are actually multiple messages
                        # separated by a newline
                        messages = message.split("\n")
                        if messages and messages[0] and messages[0][0] == ">":
                            room = messages.pop(0)[1:]
                        else:
                            room = ""

                        for single_message in messages:
                            if single_message:
                                asyncio.create_task(
                                    self.handle_message(room, single_message)
                                )
        finally:
            self.print("Connection closed.")
            await self.conn.close()
            self.connected = False

    async def handle_message(self, room: str, msg_str: str) -> None:
        """Handles a message from the server.

        Iterates through all the loaded plugins, determines whether
        any of them can handle the message, and if so, calls the
        response method of the plugin.

        Args:
            room (str): The room the message was sent from.
            msg_str (str): The message received.
        """
        self.print("<< " + msg_str)
        m = message.parse_message(room, msg_str)

        is_old_message = False
        if isinstance(m, message.ChatMessage):
            if room in self.rooms:
                r = self.rooms[room]
                if r.join_time is not None and m.timestamp is not None:
                    if m.timestamp < r.join_time:
                        # sent before we got here
                        is_old_message = True

        for plugin in self.plugins:
            if is_old_message and not plugin.scrollback_access:
                continue
            try:
                matched = await plugin.match(m)
                if matched:
                    resp = await plugin.response(m)
                    if resp:
                        if isinstance(m, message.PMMessage):
                            await self.send_pm(m.user.name, resp)
                        else:
                            await self.send(m.room, resp)
            except Exception as e:
                plg = plugin.__class__.__name__
                self.print("Error handling message in plugin {}: {}".format(plg, e))
                msg = str(e) + ": " + e.__doc__ if e.__doc__ is not None else str(e)
                self.print(msg)

    async def join(self, room: str) -> None:
        """Joins the given room.

        Args:
            room (str): The room to join.
        """
        await self.send("", f"/join {room}")

    async def leave(self, room: str) -> None:
        """Leaves the given room.

        Args:
            room (str): The room to leave.
        """
        await self.send(room, "/leave")

    @staticmethod
    def print(msg) -> None:
        """Prints a message. Intended to be possible to be overridden.

        Args:
            msg (str): The message to be printed.
        """
        print(msg)

    def __str__(self) -> str:
        """Returns a string representation of the client.

        Returns:
            str: The string representation of the client.
        """
        return "Client({})".format(self.conn.url)

    def __repr__(self) -> str:
        """Returns a representation of the client.

        Returns:
            str: The representation of the client.
        """
        return self.__str__()
