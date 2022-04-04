from pyshowdown import room
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message
from pyshowdown.user import User
from pyshowdown.utils import to_id


class UsersHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a users message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a users message, False otherwise.
        """
        return message.type == "users"
    
    async def response(self, message: Message) -> None:
        """Sets the room users in the Client's room dict.

        Args:
            message (Message): The users message.
        """
        r = room.Room(message.room)
        self.client.rooms[r.id].users = message.users


class JoinHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a join message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a join message, False otherwise.
        """
        return message.type in ["join", "j"]
    
    async def response(self, message: Message) -> None:
        """Adds the user to the room's users.

        Args:
            message (Message): The join message.
        """
        r = room.Room(message.room)
        user = User(message.user, message.rank, "", False)
        self.client.rooms[r.id].users[user.id] = user


class LeaveHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a leave message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a leave message, False otherwise.
        """
        return message.type in ["leave", "l"]
    
    async def response(self, message: Message) -> None:
        """Removes the user from the room's users.

        Args:
            message (Message): The leave message.
        """
        r = room.Room(message.room)
        del self.client.rooms[r.id].users[to_id(message.user)]


def setup(client) -> list:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        list: A list of plugins to load.
    """
    return [UsersHandler(client), JoinHandler(client), LeaveHandler(client)]