from typing import Optional, Dict

from pyshowdown.user import User


class Room:
    def __init__(self, id: str):
        """Represents a PS room.

        Args:
            id (str): The room ID.
        """
        self.id = id
        self.title: Optional[str] = None
        self.users: Dict[str, User] = {}
        self.is_battle = self.id.startswith("battle-")
        if self.is_battle:
            self.is_private_battle = self.id.count("-") == 3

            if self.is_private_battle:
                # strip the password and store separately
                self.password = self.id.split("-")[-1]
                self.id = self.id.replace("-" + self.password, "")

    def __str__(self) -> str:
        return "Room({})".format(self.id)

    def __repr__(self) -> str:
        return self.__str__()
