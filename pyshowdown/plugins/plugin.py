from pyshowdown.client import Client


class BasePlugin:
    def __init__(self, client: Client):
        """Initializes the plugin.

        Args:
            client (Client): A reference to the client.
        """
        self.client = client

    async def match(self, message):
        """Returns True if the message is a match for the plugin.

        Args:
            message (Message): The message to check.

        Raises:
            NotImplementedError: Always, since this is a base class.
        """
        raise NotImplementedError()

    async def response(self, message):
        """Returns the response for the message.

        Args:
            message (Message): The message to respond to.

        Raises:
            NotImplementedError: Always, since this is a base class.
        """
        raise NotImplementedError()
