import ssl
from typing import Optional

import aiohttp


class Connection:
    def __init__(
        self,
        url: str,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """Create a connection to the server.

        Args:
            url (str): The url to connect to.
            ssl_context (ssl.SSLContext, optional): The SSL context. Defaults to None.
        """
        self.url = url
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.ssl_context = ssl_context

    async def connect(self) -> None:
        """Connect to the server."""
        self.session = aiohttp.ClientSession()
        print("connecting...")
        if self.ssl_context is not None:
            self.ws = await self.session.ws_connect(self.url, ssl=self.ssl_context)
        else:
            self.ws = await self.session.ws_connect(self.url)

    async def send(self, message: str) -> None:
        """Send a message to the server.

        Args:
            message (str): The message to send.

        Raises:
            ConnectionError: If no connection is established.
        """
        if self.ws is None:
            raise ConnectionError("Not connected to server.")
        await self.ws.send_str(message)

    async def receive(self) -> aiohttp.WSMessage:
        """Receive a message from the server.

        Returns:
            aiohttp.WSMessage: The message received.

        Raises:
            ConnectionError: If no connection is established.
        """
        if self.ws is None:
            raise ConnectionError("Not connected to server.")
        return await self.ws.receive()

    async def close(self) -> None:
        """Close the connection to the server.

        Raises:
            ConnectionError: If no connection is established.
        """
        if self.ws is None:
            raise ConnectionError("Not connected to server.")
        await self.ws.close()

    def __str__(self) -> str:
        """Return a string representation of the connection.

        Returns:
            str: The string representation of the connection.
        """
        return "Connection: {}".format(self.url)

    def __repr__(self) -> str:
        """Return a representation of the connection.

        Returns:
            str: The representation of the connection.
        """
        return self.__str__()
