import copy
from .util import POKEMON_TYPES

class GameObject:
    def __init__(self, id_, template):
        self.id = id_
        self.template = template
        self.name = "?"
    
    def __str__(self):
        return self.template

class GameMasterObject(GameObject):
    def __init__(self, id_, template, gamemaster_entry, settings_name=""):
        super().__init__(id_, template)
        if "data" in gamemaster_entry:
            self.raw = gamemaster_entry.get("data", {}).get(settings_name, {})
        else:
            self.raw = gamemaster_entry

class Type(GameObject):
    pass

class Item(GameObject):
    pass

class Move(GameMasterObject):
    def __init__(self, template, gamemaster_entry, move_id):
        super().__init__(move_id, template, gamemaster_entry)
        self.type = None

class Grunt(GameMasterObject):
    def __init__(self, id_, template, entry, pogoinfo_data, team):
        super().__init__(id_, template, entry)

        if self.raw.get("isMale", False):
            self.gender = 1
        else:
            self.gender = 0

        self.boss = False
        self.type = None

        self.active = pogoinfo_data.get("active", False)
        self.team = team
        self.__reward_positions = pogoinfo_data.get("lineup", {}).get("rewards", [])

    @property
    def rewards(self):
        rewards = []
        for index in self.__reward_positions:
            rewards += self.team[index]
        return rewards

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

class Pokemon(GameMasterObject):
    def __init__(self, gamemaster_entry, form_id, template, mon_id):
        super().__init__(mon_id, template, gamemaster_entry)

        self.form = form_id
        self.base_template = self.raw.get("pokemonId", "")

        self.quick_moves = []
        self.charge_moves = []
        self.types = []
        self.evolutions = []
        self.temp_evolutions = []
        self._make_stats()

        self.costume = 0

        self.asset_value = None
        self.asset_suffix = None
        self._gen_asset()

        self.temp_evolution_id = 0
        self.temp_evolution_template = ""

        if self.template == self.base_template:
            self.type = POKEMON_TYPES[0]
        else:
            self.type = POKEMON_TYPES[1]

    def copy(self):
        return copy.deepcopy(self)

    @property
    def moves(self):
        return self.quick_moves + self.charge_moves

    def _gen_asset(self):
        self.asset = "pokemon_icon_"
        if self.asset_suffix:
            self.asset += str(self.asset_suffix)
        else:
            self.asset += str(self.id).zfill(3) + "_"
            if self.asset_value:
                self.asset += str(self.asset_value)
            else:
                self.asset += "00"
                if self.costume:
                    self.asset += "_" + str(self.costume).zfill(2)

    def _make_stats(self):
        self.stats = [v for v in self.raw.get("stats", {}).values()]
