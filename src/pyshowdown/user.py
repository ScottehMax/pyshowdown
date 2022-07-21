from pyshowdown.utils import to_id


RANKS = set(["&", "#", "★", "@", "%", "§", "*", "☆", "+", "^", " "])


class User:
    def __init__(self, name: str, rank: str, status: str, away: bool):
        """Represents a user.

        Args:
            name (str): The user's name.
            rank (str): The user's rank.
            status (str): The user's status.
            away (bool): Whether the user is away.
        """
        self.id = to_id(name)
        self.name = name
        self.rank = rank
        self.status = status
        self.away = away

    def __str__(self) -> str:
        return "User({}{})".format(self.rank, self.name)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.rank == other.rank
            and self.status == other.status
            and self.away == other.away
        )
