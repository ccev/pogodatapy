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

