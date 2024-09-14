import asyncio
import configparser
import importlib
import os
import ssl
import sys
from http.cookies import SimpleCookie
from typing import Optional, List, Dict, TYPE_CHECKING

import aiohttp

from pyshowdown import connection, message


if TYPE_CHECKING:
    from pyshowdown.plugins.plugin import BasePlugin
    from pyshowdown.room import Room


class Client:
    def __init__(
        self,
        username: str,
        password: str,
        url: str,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """Client class constructor.

        Args:
            username (str): The username to use.
            password (str): The password to use.
            url (str): The url to connect to.
            ssl_context (ssl.SSLContext, optional): The SSL context. Defaults to None.
        """
        self.conn = connection.Connection(url, ssl_context=ssl_context)
        self.username = username
        self.password = password
        self.connected = False
        self.cookies: Optional[SimpleCookie[str]] = None
        self.load_config()
        self.plugins: List["BasePlugin"] = []
        self.load_plugins()
        self.rooms: Dict[str, "Room"] = {}
        self.logging_in: bool = False
        self.backoff: int = 1

    def load_config(self) -> None:
        """Load config from config.ini."""
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.plugin_dir = self.config["user"].get("plugin_dir", "system")
        self.plugin_list = self.config["user"].get("plugins").split(",")

    async def connect(self) -> None:
        """Connect to the server."""
        await self.conn.connect()

    async def keep_connected(self) -> None:
        """Keeps the client connected to the server."""
        self.connected = False
        self.backoff = 1
        while not self.connected:
            try:
                await asyncio.sleep(self.backoff)
                await self.connect()
                self.connected = True
                await self.receive_forever()
            except Exception as e:
                print(e)
            self.backoff *= 2

    async def close(self) -> None:
        """Close the connection."""
        await self.conn.close()

    async def send(self, room: str, message: str) -> None:
        """Sends message to the server.

        Args:
            message (str): The message to send.
        """
        m = f"{room}|{message}"
        print(">> " + m)
        await self.conn.send(m)

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
                                await self.handle_message(room, single_message)
        finally:
            print("Connection closed.")
            await self.conn.close()
            self.connected = False

    def load_plugins(self) -> None:
        """Loads all the plugins from the directory set in config.

        It should first import them, then instantiate the class
        which is a subclass of BasePlugin.
        """
        print("Loading plugins...")

        # always load the system plugins
        sys.path.append(os.path.join(os.path.dirname(__file__), "plugins"))

        if self.plugin_dir != "system":
            sys.path.append(self.plugin_dir)

        for plugin_name in self.plugin_list:
            try:
                plugin_module = importlib.import_module(plugin_name)
                plugins = plugin_module.setup(self)
                for plugin in plugins:
                    self.plugins.append(plugin)
            except Exception as e:
                print("Error loading plugin {}: {}".format(plugin_name, e))

    async def handle_message(self, room: str, msg_str: str) -> None:
        """Handles a message from the server.

        Iterates through all the loaded plugins, determines whether
        any of them can handle the message, and if so, calls the
        response method of the plugin.

        Args:
            room (str): The room the message was sent from.
            msg_str (str): The message received.
        """
        print("<< " + msg_str)
        m = message.Message(room, msg_str)

        for plugin in self.plugins:
            try:
                matched = await plugin.match(m)
                if matched:
                    resp = await plugin.response(m)
                    if resp:
                        if m.type == "pm":
                            if m.user is not None:
                                await self.send_pm(m.user, resp)
                        else:
                            await self.send(m.room, resp)
            except Exception as e:
                plg = plugin.__class__.__name__
                print("Error handling message in plugin {}: {}".format(plg, e))
                msg = str(e) + ": " + e.__doc__ if e.__doc__ is not None else str(e)
                if m.user is not None:
                    await self.send_pm(m.user, msg)

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

    def __str__(self) -> str:
        """Returns a string representation of the client.

        Returns:
            str: The string representation of the client.
        """
        return "Client({})".format(
            self.conn.url
        )

    def __repr__(self) -> str:
        """Returns a representation of the client.

        Returns:
            str: The representation of the client.
        """
        return self.__str__()
