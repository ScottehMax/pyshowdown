from typing import List

from pyshowdown import room
from pyshowdown.client import Client
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message


class InitHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is an init message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is an init message, False otherwise.
        """
        return message.type == "init"

    async def response(self, message: Message) -> None:
        """Creates the room in the Client's room dict.

        Args:
            message (Message): The init message.
        """
        r = room.Room(message.room)
        self.client.rooms[r.id] = r


def setup(client: Client) -> List[BasePlugin]:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        List[BasePlugin]: A list of plugins to load.
    """
    return [InitHandler(client)]
