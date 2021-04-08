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

