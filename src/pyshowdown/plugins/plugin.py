from typing import Generic, Optional, TypeVar

from pyshowdown.client import Client
from pyshowdown.message import Message

MessageType = TypeVar("MessageType", bound=Message)


class BasePlugin(Generic[MessageType]):
    # whether the plugin should respond to messages sent before joining the room
    scrollback_access: bool = False

    def __init__(self, client: Client):
        """Initializes the plugin.

        Args:
            client (Client): A reference to the client.
        """
        self.client = client

    async def match(self, message: Message) -> bool:
        """Returns True if the message is a match for the plugin.

        Args:
            message (Message): The message to check.

        Raises:
            NotImplementedError: Always, since this is a base class.

        Returns:
            bool: True if the message is a match, False otherwise.
        """
        raise NotImplementedError()

    async def response(self, message: MessageType) -> Optional[str]:
        """Returns the response for the message.

        Args:
            message (MessageType): The message to respond to.

        Raises:
            NotImplementedError: Always, since this is a base class.

        Returns:
            Optional[str]: The response for the message.
        """
        raise NotImplementedError()
