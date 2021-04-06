from .enums import BasicType, QuestType

class GameObject:
    def __init__(self, id_, template):
        self.id = id_
        self.template = template
        self.name = "?"
    
    def __str__(self):
        return self.template

    def __bool__(self):
        return bool(self.id)

class GameMasterObject(GameObject):
    def __init__(self, id_, template, gamemaster_entry, settings_name=""):
        super().__init__(id_, template)
        if "data" in gamemaster_entry:
            self.raw = gamemaster_entry.get("data", {}).get(settings_name, {})
        else:
            self.raw = gamemaster_entry

class Type(GameObject):
    pass

class Move(GameMasterObject):
    def __init__(self, template, gamemaster_entry, move_id):
        super().__init__(move_id, template, gamemaster_entry)
        self.type = None

class Weather(GameMasterObject):
    def __init__(self, template, entry, wid):
        super().__init__(wid, template, entry)
        self.type_boosts = []

class Quest:
    def __init__(self):
        pass


class RaidIterator:
    def __init__(self, raids):
        self.mons = []
        for level, mon in raids.items():
            self.mons += [(level, m) for m in mon]
        self._index = 0

    def __next__(self):
        if self._index < len(self.mons):
            result = self.mons[self._index]
            self._index += 1
            return result
        raise StopIteration

class Raids:
    def __init__(self):
        self.raids = {}

    def add_mon(self, level, mon):
        level = int(level)
        if level not in self.raids:
            self.raids[level] = []
        
        self.raids[level].append(mon)

    def __iter__(self):
        return RaidIterator(self.raids)

    def __getitem__(self, key):
        return self.raids.get(key, [])
