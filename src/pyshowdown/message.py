import json
from typing import Optional, List, Dict

from pyshowdown.user import User, RANKS


class Message:
    def __init__(self, room: str, message_str: str):
        """Initialize a Message object.

        Args:
            room (str): The room the message was sent to.
            message_str (str): The raw message.
        """
        self.room = room
        self.message_str = message_str

    def __str__(self) -> str:
        """Return a string representation of the message.

        Returns:
            str: A string representation of the message.
        """
        return f"<{self.__class__}: {self.message_str}>"

    def __repr__(self) -> str:
        """Return a representation of the message.

        Returns:
            str: A representation of the message.
        """
        return self.__str__()


section = Dict[str, List[str]]
formats = Dict[str, section]


def parse_formats(format_str: str) -> formats:
    """Parse a format message and return a list of formats.

    Args:
        format_str (str): The format message.

    Returns:
        formats: A dictionary of sections, formats, and some additional
            info about the formats.
    """
    results: formats = {}
    split_str = format_str.split("|")
    in_section = False
    section_name = ""

    for item in split_str:
        if not item:
            continue
        if in_section:
            section_name = item
            results[section_name] = {}
            in_section = False
        elif item[0] == ",":
            if item[1:] == "LL":
                # this is being run locally, ignore it
                continue
            # this is a section
            in_section = True
            column_number = int(item[1:])  # unused here for now
        else:
            # this is a format
            info = item.split(",")
            name, rule_num_str = ",".join(info[0:-1]), info[-1]
            rule_num = int(rule_num_str, 16)
            rules = []

            if rule_num & 1:
                rules.append("Requires Team")
            if rule_num & 2:
                rules.append("Available for Search")
            if rule_num & 4:
                rules.append("Available for Challenge")
            if rule_num & 8:
                rules.append("Available for Tournaments")
            if rule_num & 16:
                rules.append("Level 50")
            results[section_name][name] = rules

    return results


class InitMessage(Message):
    def __init__(self, room: str, message_str: str, roomtype: str):
        super().__init__(room, message_str)
        self.roomtype = roomtype


class DeinitMessage(Message):
    def __init__(self, room: str, message_str: str):
        super().__init__(room, message_str)


class TitleMessage(Message):
    def __init__(self, room: str, message_str: str, title: str):
        super().__init__(room, message_str)
        self.title = title


class UsersMessage(Message):
    def __init__(
        self, room: str, message_str: str, usercount: int, users: Dict[str, User]
    ):
        super().__init__(room, message_str)
        self.usercount = usercount
        self.users = users


class HTMLMessage(Message):
    def __init__(self, room: str, message_str: str, html: str):
        super().__init__(room, message_str)
        self.html = html


class UHTMLMessage(Message):
    def __init__(self, room: str, message_str: str, name: str, html: str):
        super().__init__(room, message_str)
        self.name = name
        self.html = html


class UHTMLChangeMessage(Message):
    def __init__(self, room: str, message_str: str, name: str, html: str):
        super().__init__(room, message_str)
        self.name = name
        self.html = html


class JoinMessage(Message):
    def __init__(self, room: str, message_str: str, user: User):
        super().__init__(room, message_str)
        self.user = user


class LeaveMessage(Message):
    def __init__(self, room: str, message_str: str, user: User):
        super().__init__(room, message_str)
        self.user = user


class RenameMessage(Message):
    def __init__(
        self, room: str, message_str: str, user: User, oldid: str, status_str: str
    ):
        super().__init__(room, message_str)
        self.user = user
        self.oldid = oldid
        self.status_str = status_str


class ChatMessage(Message):
    def __init__(
        self,
        room: str,
        message_str: str,
        user: User,
        message: str,
        timestamp: Optional[int] = None,
    ):
        super().__init__(room, message_str)
        self.user = user
        self.message = message
        self.timestamp = timestamp


class TimestampMessage(Message):
    def __init__(self, room: str, message_str: str, timestamp: int):
        super().__init__(room, message_str)
        self.timestamp = timestamp


class BattleMessage(Message):
    def __init__(
        self, room: str, message_str: str, roomid: str, user1: str, user2: str
    ):
        super().__init__(room, message_str)
        self.roomid = roomid
        self.user1 = user1
        self.user2 = user2


class PopupMessage(Message):
    def __init__(self, room: str, message_str: str, message: str):
        super().__init__(room, message_str)
        self.message = message


class PMMessage(Message):
    def __init__(
        self, room: str, message_str: str, user: User, receiver: User, message: str
    ):
        super().__init__(room, message_str)
        self.user = user
        self.receiver = receiver
        self.message = message


class UserCountMessage(Message):
    def __init__(self, room: str, message_str: str, usercount: int):
        super().__init__(room, message_str)
        self.usercount = usercount


class NameTakenMessage(Message):
    def __init__(self, room: str, message_str: str, user: User, message: str):
        super().__init__(room, message_str)
        self.user = user
        self.message = message


class ChallstrMessage(Message):
    def __init__(self, room: str, message_str: str, challstr: str):
        super().__init__(room, message_str)
        self.challstr = challstr


class UpdateUserMessage(Message):
    def __init__(
        self,
        room: str,
        message_str: str,
        user: User,
        named: bool,
        avatar: str,
        settings: Dict[str, str],
    ):
        super().__init__(room, message_str)
        self.user = user
        self.named = named
        self.avatar = avatar
        self.settings = settings


class FormatsMessage(Message):
    def __init__(self, room: str, message_str: str, formats: formats):
        super().__init__(room, message_str)
        self.formats = formats


class UpdateSearchMessage(Message):
    def __init__(self, room: str, message_str: str, json: Dict[str, str]):
        super().__init__(room, message_str)
        self.json = json


class UpdateChallengesMessage(Message):
    def __init__(self, room: str, message_str: str, json: Dict[str, str]):
        super().__init__(room, message_str)
        self.json = json


class QueryResponseMessage(Message):
    def __init__(
        self, room: str, message_str: str, query_type: str, json_data: Dict[str, str]
    ):
        super().__init__(room, message_str)
        self.query_type = query_type
        self.json_data = json_data
        self.password = None

    def handle(self):
        if self.query_type == "savereplay":
            # override the relevant room, since queryresponse messages
            # are sent as global messages
            self.room = self.json_data["id"]
            self.password = self.json_data.get("password", "")


class RawMessage(Message):
    def __init__(self, room: str, message_str: str, data: str):
        super().__init__(room, message_str)
        self.data = data


class WinMessage(Message):
    def __init__(self, room: str, message_str: str, winner: str):
        super().__init__(room, message_str)
        self.winner = winner


class PlayerMessage(Message):
    def __init__(
        self,
        room: str,
        message_str: str,
        player: Optional[str],
        name: Optional[str],
        avatar: Optional[str],
        rating: Optional[int],
    ):
        super().__init__(room, message_str)
        self.player = player
        self.name = name
        self.avatar = avatar
        self.rating = rating


class PageHTMLMessage(Message):
    def __init__(self, room: str, message_str: str, html: str):
        super().__init__(room, message_str)
        self.html = html


class ErrorMessage(Message):
    def __init__(self, room: str, message_str: str, error: str):
        super().__init__(room, message_str)
        self.error = error


def parse_message(room: str, message_str: str) -> Message:
    info = message_str.split("|")
    if len(info) > 1:
        message_type = info[1]
    else:
        message_type = None

    if message_type == "init":
        return InitMessage(room, message_str, info[2])

    elif message_type == "deinit":
        return DeinitMessage(room, message_str)

    elif message_type == "title":
        return TitleMessage(room, message_str, info[2])

    elif message_type == "users":
        users = info[2].split(",")
        usercount = int(users.pop(0))

        users_dict = {}

        for u in users:
            if "@" in u[1:]:
                s = u[1:].split("@")
                name, status = (s[0], "@".join(s[1:]))
            else:
                name, status = u[1:], ""

            away = False
            if status:
                if status[0] == "!":
                    away = True
                    status = status[1:]

            user_obj = User(name, u[0], status, away)
            users_dict[user_obj.id] = user_obj

        return UsersMessage(room, message_str, usercount, users_dict)

    elif message_type == "html":
        return HTMLMessage(room, message_str, info[2])

    elif message_type == "uhtml":
        return UHTMLMessage(room, message_str, info[2], info[3])

    elif message_type == "uhtmlchange":
        return UHTMLChangeMessage(room, message_str, info[2], info[3])

    elif message_type in ["j", "J", "join"]:
        u = info[2]
        if "@" in u[1:]:
            s = u[1:].split("@")
            name, status = (s[0], "@".join(s[1:]))
        else:
            name, status = u[1:], ""

        away = False
        if status:
            if status[0] == "!":
                away = True
                status = status[1:]

        user = User(name, u[0], status, away)
        return JoinMessage(room, message_str, user)

    elif message_type in ["l", "L", "leave"]:
        user = User(info[2][1:], info[2][0], "", False)
        return LeaveMessage(room, message_str, user)

    elif message_type in ["n", "N", "name"]:
        u = info[2]
        oldid = info[3]

        if "@" in u[1:]:
            s = u[1:].split("@")
            name, status = (s[0], "@".join(s[1:]))
        else:
            name, status = u[1:], ""

        status_str = status

        away = False
        if status:
            if status[0] == "!":
                away = True
                status = status[1:]

        user = User(name, u[0], status, away)
        return RenameMessage(room, message_str, user, oldid, status_str)

    elif message_type in ["c", "chat"]:
        rank, name = info[2][0], info[2][1:]
        message = "|".join(info[3:])
        user = User(name, rank, "", False)
        return ChatMessage(room, message_str, user, message)

    elif message_type == "c:":
        timestamp = int(info[2])
        rank, name = info[3][0], info[3][1:]
        message = "|".join(info[4:])
        user = User(name, rank, "", False)
        return ChatMessage(room, message_str, user, message, timestamp)

    elif message_type == ":":
        timestamp = int(info[2])
        return TimestampMessage(room, message_str, timestamp)

    elif message_type == "battle":
        roomid = info[2]
        user1 = info[3]
        user2 = info[4]
        return BattleMessage(room, message_str, roomid, user1, user2)

    elif message_type == "popup":
        message = "|".join(info[2:])
        return PopupMessage(room, message_str, message)

    elif message_type == "pm":
        user_str = info[2]
        receiver_str = info[3]
        message = "|".join(info[4:])
        user = User(user_str[1:], user_str[0], "", False)
        receiver = User(receiver_str[1:], receiver_str[0], "", False)
        return PMMessage(room, message_str, user, receiver, message)

    elif message_type == "usercount":
        usercount = int(info[2])
        return UserCountMessage(room, message_str, usercount)

    elif message_type == "nametaken":
        rank, name = info[2][0], info[2][1:]
        message = info[3]
        user = User(name, rank, "", False)
        return NameTakenMessage(room, message_str, user, message)

    elif message_type == "challstr":
        challstr = "|".join(info[2:])
        return ChallstrMessage(room, message_str, challstr)

    elif message_type == "updateuser":
        rank, name = info[2][0], info[2][1:]
        named = True if info[3] == "1" else False
        avatar = info[4]
        settings = json.loads(info[5])
        user = User(name, rank, "", False)
        return UpdateUserMessage(room, message_str, user, named, avatar, settings)

    elif message_type == "formats":
        formats = parse_formats("|".join(info[2:]))
        return FormatsMessage(room, message_str, formats)

    elif message_type == "updatesearch":
        json_data = json.loads("|".join(info[2:]))
        return UpdateSearchMessage(room, message_str, json_data)

    elif message_type == "updatechallenges":
        json_data = json.loads("|".join(info[2:]))
        return UpdateChallengesMessage(room, message_str, json_data)

    elif message_type == "queryresponse":
        query_type = info[2]
        json_data = json.loads("|".join(info[3:]))
        m = QueryResponseMessage(room, message_str, query_type, json_data)
        m.handle()
        return m

    elif message_type == "raw":
        data = info[2]
        return RawMessage(room, message_str, data)

    elif message_type == "win":
        winner = info[2]
        return WinMessage(room, message_str, winner)

    elif message_type == "player":
        player = info[2] if len(info) > 2 else None
        name = info[3] if len(info) > 3 else None
        avatar = info[4] if len(info) > 4 else None
        rating = int(info[5]) if len(info) > 5 and info[5] else None
        return PlayerMessage(room, message_str, player, name, avatar, rating)

    elif message_type == "pagehtml":
        html = "|".join(info[2:])
        return PageHTMLMessage(room, message_str, html)

    elif message_type == "error":
        error = "|".join(info[2:])
        return ErrorMessage(room, message_str, error)

    else:
        return Message(room, message_str)
