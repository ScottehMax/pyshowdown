from pyshowdown.utils import to_id

class User:
    def __init__(self, name, rank, status, away):
        self.id = to_id(name)
        self.name = name
        self.rank = rank
        self.status = status
        self.away = away
    
    def __str__(self):
        return "User({}{})".format(self.rank, self.name)
    
    def __repr__(self):
        return self.__str__()