from typing import Optional
from . import connection
from . import message
import asyncio
import ssl
import aiohttp
import json
import configparser


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

    def load_config(self):
        """Load config from config.ini.
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.username = config['user']['username']
        self.password = config['user']['password']

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

    async def handle_message(self, msg_str: str):
        """Handles a message from the server.

        Args:
            msg_str (str): The message received.
        """
        print(msg_str)
        m = message.Message("", msg_str)

        if m.type == "challstr":
            await self.handle_challstr(m.challstr)

    async def handle_challstr(self, challstr: str):
        """Handle the server's challstr message to log in."""
        print("Got challstr! Trying to log in...")
        base_url = "https://play.pokemonshowdown.com/action.php"
        data = {
            "act": "login",
            "name": self.username,
            "pass": self.password,
            "challstr": challstr,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, data=data) as resp:
                result = await resp.text()
                self.cookies = resp.cookies
                print('----------')
                print(self.cookies)
                print('----------')

                # strip the leading [
                result = result[1:]
                result = json.loads(result)

                await self.send("", "/trn {},0,{}".format(self.username, result["assertion"]))

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
