from pyshowdown.utils import to_id


RANKS = set(["~", "&", "#", "★", "*", "@", "%", "☆", "§", "+", "^", " ", "!", "‽"])
RANK_ORDER = {
    "~": 101,
    "#": 102,
    "&": 103,
    "★": 104,
    "@": 105,
    "%": 106,
    "§": 107,
    "_": 108,
    "*": 109,
    "☆": 110,
    "+": 200,
    " ": 201,
    "!": 301,
    "✖": 302,
    "‽": 303,
}


class User:
    def __init__(self, name: str, rank: str, status: str, away: bool):
        """Represents a user.

        Args:
            name (str): The user's name, without rank.
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

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        # first, compare by rank
        if self.rank != other.rank:
            return RANK_ORDER.get(self.rank, 108) > RANK_ORDER.get(other.rank, 108)
        # then, compare by away status
        if self.away != other.away:
            return self.away
        # finally, compare by name, case-insensitive
        return self.name.lower() > other.name.lower()

    def to_string(self) -> str:
        """Return the user's name with rank and status."""
        if self.status or self.away:
            status_str = "@" + ("!" if self.away else "") + self.status
        else:
            status_str = ""
        return "{}{}{}".format(self.rank, self.name, status_str)

    @property
    def fullname(self) -> str:
        """Return the user's name with rank."""
        return "{}{}".format(self.rank, self.name)
