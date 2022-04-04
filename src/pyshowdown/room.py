class Room:
    def __init__(self, id):
        self.id = id
        self.users = {}
        self.is_battle = self.id.startswith("battle-")
        if self.is_battle:
            self.is_private_battle = self.id.count("-") == 3
            
            if self.is_private_battle:
                # strip the password and store separately
                self.password = self.id.split("-")[-1]
                self.id = self.id.replace("-" + self.password, "")

    def __str__(self):
        return "Room({})".format(self.id)

    def __repr__(self):
        return self.__str__()