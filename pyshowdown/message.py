import json


class Message:
    def __init__(self, room: str, message_str: str):
        """Initialize a Message object.

        Args:
            room (str): The room the message was sent to.
            message_str (str): The raw message.
        """
        self.room = room
        self.message_str = message_str
        self.parse_message()

    def parse_message(self):
        """Parse the message and store the attributes."""
        info = self.message_str.split("|")
        self.type = info[1]

        # Room initialization
        if self.type == "init":
            self.roomtype = info[2]

        elif self.type == "title":
            self.title = info[2]

        elif self.type == "users":
            users = info[2].split(",")
            self.usercount = int(users.pop(0))

            self.users = []

            # this should probably be refactored to use User objects
            for u in users:
                rank = u[0]
                u = u[1:]
                if "@" in u:
                    name, status = u.split("@")
                else:
                    name, status = u, ""

                if status and status[0] == "!":
                    away = True
                    status = status[1:]
                else:
                    away = False

                self.users.append((rank, name, status, away))

        # Room messages
        elif self.type == "html":
            self.html = info[2]

        elif self.type == "uhtml":
            self.name = info[2]
            self.html = info[3]

        elif self.type == "uhtmlchange":
            self.name = info[2]
            self.html = info[3]

        elif self.type in ["j", "J", "join"]:
            self.type = "join"
            self.user = info[2]

        elif self.type in ["l", "L", "leave"]:
            self.type = "leave"
            self.user = info[2]

        elif self.type in ["n", "N", "name"]:
            self.type = "name"
            self.user = info[2]
            self.oldid = info[3]

        elif self.type in ["c", "chat"]:
            self.type = "chat"
            self.timestamp = None
            self.user = info[2]
            self.message = info[3]

        elif self.type == ":":
            self.type = "timestamp"
            self.timestamp = int(info[2])

        elif self.type == "c:":
            self.type = "chat"
            self.timestamp = int(info[2])
            self.user = info[3]
            self.message = info[4]

        elif self.type == "battle":
            self.roomid = info[2]
            self.user1 = info[3]
            self.user2 = info[4]

        # Global messages
        elif self.type == "popup":
            self.message = info[2]

        elif self.type == "pm":
            self.sender = info[2]
            self.receiver = info[3]
            self.message = info[4]

        elif self.type == "usercount":
            self.usercount = int(info[2])

        elif self.type == "nametaken":
            self.username = info[2]
            self.message = info[3]

        elif self.type == "challstr":
            self.challstr = "|".join(info[2:])

        elif self.type == "updateuser":
            self.user = info[2]
            self.named = True if info[3] == "1" else False
            self.avatar = info[4]
            self.settings = json.loads(info[5])

        elif self.type == "formats":
            self.formats = parse_formats("|".join(info[2:]))

        elif self.type == "updatesearch":
            self.json = json.loads("|".join(info[2:]))

        elif self.type == "updatechallenges":
            self.json = json.loads("|".join(info[2:]))

        elif self.type == "queryresponse":
            self.query_type = info[2]

            json_str = "|".join(info[3:])
            self.json_data = json.loads(json_str)

            if self.query_type == "savereplay":
                # override the relevant room, since queryresponse messages
                # are sent as global messages
                self.room = self.json_data["id"]

        elif self.type == "raw":
            self.data = info[2]

        # Battle messages
        elif self.type == "win":
            self.winner = info[2]

        else:
            # TODO: Handle other message types
            pass

    def __str__(self) -> str:
        """Return a string representation of the message.

        Returns:
            str: A string representation of the message.
        """
        return f"<Message: {self.message_str}>"

    def __repr__(self) -> str:
        """Return a representation of the message.

        Returns:
            str: A representation of the message.
        """
        return self.__str__()


def parse_formats(format_str: str) -> dict:
    """Parse a format message and return a list of formats.

    Args:
        format_str (str): The format message.

    Returns:
        dict: A dictionary of sections, formats, and some additional
            info about the formats.
    """
    results = {}
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
            # this is a section
            in_section = True
            section_number = int(item[1:])
        else:
            # this is a format
            name, rule_num = item.split(",")
            rule_num = int(rule_num, 16)
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
