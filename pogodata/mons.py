import re
import copy
from .game_objects import GameObject, GameMasterObject
from .util import gen_uicon, POKEMON_TYPES

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