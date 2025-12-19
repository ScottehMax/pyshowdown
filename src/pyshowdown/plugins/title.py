from typing import List

from pyshowdown import room
from pyshowdown.client import Client
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message, TitleMessage


class TitleHandler(BasePlugin[TitleMessage]):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a title message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a title message, False otherwise.
        """
        return isinstance(message, TitleMessage)

    async def response(self, message: TitleMessage) -> None:
        """Sets the room title in the Client's room dict.

        Args:
            message (TitleMessage): The title message.
        """
        r = room.Room(message.room)
        self.client.rooms[r.id].title = message.title


def setup(client: Client) -> List[BasePlugin]:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        List[BasePlugin]: A list of plugins to load.
    """
    return [TitleHandler(client)]
