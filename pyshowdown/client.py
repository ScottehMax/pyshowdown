import asyncio
import configparser
import importlib
import os
import sys
import ssl
from typing import Optional

import aiohttp

from pyshowdown import connection, message


class Client:
    def __init__(
        self,
        host: str,
        port: int,
        path: str,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """Client class constructor.

        Args:
            host (str): Hostname or IP address of the server.
            port (int): The port number of the server.
            path (str): The path to the server.
            ssl_context (ssl.SSLContext, optional): The SSL context. Defaults to None.
        """
        self.conn = connection.Connection(host, port, path, ssl_context=ssl_context)
        self.connected = False
        self.load_config()
        self.plugins = []
        self.load_plugins()

    def load_config(self):
        """Load config from config.ini."""
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.username = config["user"]["username"]
        self.password = config["user"]["password"]
        self.plugin_dir = config["user"].get("plugin_dir", "system")
        self.plugin_list = config["user"].get("plugins").split(",")

    async def connect(self):
        """Connect to the server."""
        await self.conn.connect()

    async def keep_connected(self):
        """Keeps the client connected to the server."""
        self.connected = False
        timeout = 1
        while not self.connected:
            try:
                await asyncio.sleep(timeout)
                await self.connect()
                self.connected = True
                timeout = 1
                await self.receive_forever()
            except Exception as e:
                print(e)
                timeout += 1

    async def close(self):
        """Close the connection."""
        await self.conn.close()

    async def send(self, room: str, message: str):
        """Sends message to the server.

        Args:
            message (str): The message to send.
        """
        await self.conn.send(f"{room}|{message}")

    async def receive(self) -> str:
        """Receives data from the server.

        Returns:
            str: The data received.
        """
        return await self.conn.receive()

    async def receive_forever(self):
        """Receives data from the server forever."""
        async for ws_message in self.conn.ws:
            if ws_message.type == aiohttp.WSMsgType.TEXT:
                print(ws_message)
                await self.handle_message(ws_message.data)
        self.connected = False

    def load_plugins(self):
        """Loads all the plugins from the directory set in config.

        It should first import them, then instantiate the class
        which is a subclass of BasePlugin.
        """
        print("Loading plugins...")

        # always load the system plugins
        sys.path.append(os.path.join(os.path.dirname(__file__), "plugins"))

        if self.plugin_dir != "system":
            sys.path.append(self.plugin_dir)

        for plugin in self.plugin_list:
            try:
                plugin_module = importlib.import_module(plugin)
                plugins = plugin_module.setup(self)
                for plugin in plugins:
                    self.plugins.append(plugin)
            except Exception as e:
                print("Error loading plugin {}: {}".format(plugin, e))

    async def handle_message(self, msg_str: str):
        """Handles a message from the server.

        Iterates through all the loaded plugins, determines whether
        any of them can handle the message, and if so, calls the
        response method of the plugin.

        Args:
            msg_str (str): The message received.
        """
        print(msg_str)
        m = message.Message("", msg_str)

        for plugin in self.plugins:
            matched = await plugin.match(m)
            if matched:
                resp = await plugin.response(m)
                if resp:
                    await self.send(m.room, resp)

    def __str__(self) -> str:
        """Returns a string representation of the client.

        Returns:
            str: The string representation of the client.
        """
        return "Client({}, {}, {})".format(
            self.conn.host, self.conn.port, self.conn.path
        )

    def __repr__(self) -> str:
        """Returns a representation of the client.

        Returns:
            str: The representation of the client.
        """
        return self.__str__()


async def main():
    client = Client("sim3.psim.us", 8000, "/showdown/websocket")
    await client.keep_connected()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
