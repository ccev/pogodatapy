import copy
from enum import Enum

class BasicType(Enum):
    UNSET = 0
    SET = 1

class GameObject:
    def __init__(self, id_, template):
        self.id = id_
        self.template = template
        self.name = "?"
    
    def __str__(self):
        return self.template

    def __bool__(self):
        return bool(self.id)

    def copy(self):
        return copy.deepcopy(self)

class GameMasterObject(GameObject):
    def __init__(self, id_, template, gamemaster_entry, settings_name=""):
        super().__init__(id_, template)
        if "data" in gamemaster_entry:
            self.raw = gamemaster_entry.get("data", {}).get(settings_name, {})
        else:
            self.raw = gamemaster_entry

class Type(GameObject):
    def __init__(self, icon, id_, template):
        super().__init__(id_, template)
        self.__icon = icon

    @property
    def icon_url(self):
        return self.__icon.montype(self)

class PseudoObject:
    pass

class Waypoint(PseudoObject):
    def __init__(self, lat=0, lon=0, name="", url=""):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.url = url

class Pokestop(Waypoint):
    def __init__(self, lat=0, lon=0, name="", url=""):
        super().__init__(lat, lon, name, url)
        self.grunt = None
        self.lure = None
        self.quest = None

        self.ar_quest = False

class Gym(Waypoint):
    def __init__(self, lat=0, lon=0, name="", url=""):
        super().__init__(lat, lon, name, url)
        self.level = 1
        self.team = 0
        self.raid = None
