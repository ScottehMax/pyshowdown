import aiohttp
import asyncio
import ssl
from typing import Optional


class Connection:
    def __init__(
        self,
        host: str,
        port: int,
        path: str,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """Create a connection to the server.

        Args:
            host (str): The hostname of the server.
            port (int): The port of the server.
            path (str): The path to the server.
            ssl_context (ssl.SSLContext, optional): The SSL context. Defaults to None.
        """
        self.host = host
        self.port = port
        self.path = path
        self.protocol = "wss" if port == 443 else "ws"
        self.url = "{}://{}:{}{}".format(self.protocol, self.host, self.port, self.path)
        self.ws = None
        self.ssl_context = ssl_context

    async def connect(self):
        """Connect to the server."""
        self.session = aiohttp.ClientSession()
        print("connecting...")
        if self.ssl_context is not None:
            self.ws = await self.session.ws_connect(self.url, ssl=self.ssl_context)
        else:
            self.ws = await self.session.ws_connect(self.url)

    async def send(self, message: str):
        """Send a message to the server.

        Args:
            message (str): The message to send.
        """
        await self.ws.send_str(message)

    async def receive(self):
        """Receive a message from the server.

        Returns:
            str: The message received.
        """
        return await self.ws.receive()

    async def close(self):
        """Close the connection to the server."""
        await self.ws.close()

    def __str__(self):
        """Return a string representation of the connection.

        Returns:
            str: The string representation of the connection.
        """
        return "Connection: {}".format(self.url)

    def __repr__(self):
        """Return a representation of the connection.

        Returns:
            str: The representation of the connection.
        """
        return self.__str__()
