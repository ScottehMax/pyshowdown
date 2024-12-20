from typing import List

from pyshowdown import room
from pyshowdown.client import Client
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.message import Message, UsersMessage, JoinMessage, LeaveMessage, RenameMessage
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
        return isinstance(message, UsersMessage)

    async def response(self, message: Message) -> None:
        """Sets the room users in the Client's room dict.

        Args:
            message (Message): The users message.
        """
        if isinstance(message, UsersMessage):
            r = room.Room(message.room)
            if message.users is not None:
                self.client.rooms[r.id].users = message.users


class JoinHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a join message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a join message, False otherwise.
        """
        return isinstance(message, JoinMessage)

    async def response(self, message: Message) -> None:
        """Adds the user to the room's users.

        Args:
            message (Message): The join message.
        """
        if isinstance(message, JoinMessage):
            r = room.Room(message.room)
            if message.user is not None:
                self.client.rooms[r.id].users[message.user.id] = message.user


class LeaveHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a leave message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a leave message, False otherwise.
        """
        return isinstance(message, LeaveMessage)

    async def response(self, message: Message) -> None:
        """Removes the user from the room's users.

        Args:
            message (Message): The leave message.
        """
        if isinstance(message, LeaveMessage):
            r = room.Room(message.room)
            if message.user and message.user.id in self.client.rooms[r.id].users:
                del self.client.rooms[r.id].users[message.user.id]


class RenameHandler(BasePlugin):
    async def match(self, message: Message) -> bool:
        """Returns true if the message is a rename message.

        Args:
            message (Message): The message to check.

        Returns:
            bool: True if the message is a rename message, False otherwise.
        """
        return isinstance(message, RenameMessage)

    async def response(self, message: Message) -> None:
        """Renames the user in the room's users.

        Args:
            message (Message): The rename message.
        """
        if isinstance(message, RenameMessage):
            r = room.Room(message.room)
            if to_id(message.oldid) in self.client.rooms[r.id].users:
                user = self.client.rooms[r.id].users[to_id(message.oldid)]
                if message.user is not None:
                    user.name = message.user.name
                    self.client.rooms[r.id].users[message.user.id] = user
                    del self.client.rooms[r.id].users[to_id(message.oldid)]


def setup(client: Client) -> List[BasePlugin]:
    """Return a list of plugins to load.

    Args:
        client (Client): The client to use.

    Returns:
        List[BasePlugin]: A list of plugins to load.
    """
    return [UsersHandler(client), JoinHandler(client), LeaveHandler(client), RenameHandler(client)]
