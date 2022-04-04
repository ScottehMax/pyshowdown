from pyshowdown import room
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
        self.client.rooms[message.room] = r