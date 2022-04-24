from typing import List

from pyshowdown.client import Client
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message


class DeinitHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a deinit message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a deinit message, False otherwise.
        """
        return message.type == "deinit"

    async def response(self, message: Message) -> None:
        """Removes the room from the Client's room dict.

        Args:
            message (Message): The deinit message.
        """
        del self.client.rooms[message.room]


def setup(client: Client) -> List[BasePlugin]:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        List[BasePlugin]: A list of plugins to load.
    """
    return [DeinitHandler(client)]
