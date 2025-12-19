from typing import List

from pyshowdown.client import Client
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message, DeinitMessage


class DeinitHandler(BasePlugin[DeinitMessage]):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a deinit message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a deinit message, False otherwise.
        """
        return isinstance(message, DeinitMessage)

    async def response(self, message: DeinitMessage) -> None:
        """Removes the room from the Client's room dict.

        PS also sends a deinit message if you join a room using a
        room alias (appearing as if from the alias room), so we
        should check if we have it first.

        Args:
            message (DeinitMessage): The deinit message.
        """
        if message.room in self.client.rooms:
            del self.client.rooms[message.room]


def setup(client: Client) -> List[BasePlugin]:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        List[BasePlugin]: A list of plugins to load.
    """
    return [DeinitHandler(client)]
