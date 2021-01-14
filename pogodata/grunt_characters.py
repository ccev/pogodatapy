import re
from .game_objects import GameMasterObject

class GruntCharacter(GameMasterObject):
    def __init__(self, id_, template, entry):
        super().__init__(id_, template, entry, "invasionNpcDisplaySettings")

        if self.raw.get("isMale", False):
            self.gender = 1
        else:
            self.gender = 0

        self.boss = False
        self.type = None

def make_grunt_list(pogodata):
    grunts = []
    enums = pogodata.get_enum("InvasionCharacter")
    for entry in pogodata.raw_gamemaster:
        templateid = entry["templateId"]
        if re.search(r"^CHARACTER_.*", templateid):
            grunt = GruntCharacter(enums.get(templateid, 0), templateid, entry)
            grunt.name = pogodata.get_locale(grunt.raw.get("trainerName", "combat_grunt_name"))

            if [t for t in grunt.template.split("_") if t in ["EXECUTIVE", "GIOVANNI"]]:
                grunt.boss = True
                
            grunt.type = pogodata.get_type(template=grunt.template.split("_")[1])

            grunts.append(grunt)
    return grunts
