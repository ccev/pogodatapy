import re
from .objects import GameMasterObject

class Move(GameMasterObject):
    def __init__(self, template, gamemaster_entry, move_id):
        super().__init__(move_id, template, gamemaster_entry)
        self.type = None
        self.power = self.raw.get("power", 0)
        self.energy_delta = self.raw.get("energyDelta", 0)
        self.buffs = self.raw.get("buffs", {})

def _make_move_list(pogodata):
    pogodata.moves = []
    move_enum = pogodata.get_enum("HoloPokemonMove")
    pattern = r"^COMBAT_V\d{4}_MOVE_"
    for templateid, entry in pogodata.get_gamemaster(pattern+".*", "combatMove"):
        template = re.sub(pattern, "", templateid)
        move_id = move_enum.get(template, 0)
        move = Move(template, entry, move_id)
        move.type = pogodata.get_type(template=move.raw.get("type"))
        move.name = pogodata.get_locale("move_name_" + str(move.id).zfill(4))
        pogodata.moves.append(move)