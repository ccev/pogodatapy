import re
from .game_objects import GameMasterObject

class Move(GameMasterObject):
    def __init__(self, template, gamemaster_entry):
        super().__init__(
            int(gamemaster_entry["templateId"].split("COMBAT_V")[1].split("_")[0]),
            template,
            gamemaster_entry,
            "combatMove"
        )

        self.type = None

def make_move_list(pogodata):
    moves = []
    for entry in pogodata.raw_gamemaster:
        templateid = entry["templateId"]
        if re.search(r"^COMBAT_V\d{4}_MOVE_.*", templateid):
            template = re.sub(r"^COMBAT_V\d{4}_MOVE_", "", templateid)
            move = Move(template, entry)
            move.type = pogodata.get_type(template=move.raw.get("type"))
            move.name = pogodata.get_locale("move_name_" + str(move.id).zfill(4))
            moves.append(move)
    return moves