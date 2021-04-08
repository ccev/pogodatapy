from enum import Enum
from .objects import GameMasterObject
from .misc import httpget, INFO_URL

class Gender(Enum):
    UNSET = 0
    FEMALE = 1
    MALE = 2

class Grunt(GameMasterObject):
    def __init__(self, icon, id_, template, entry, pogoinfo_data, team):
        super().__init__(id_, template, entry)

        if self.raw.get("isMale", False):
            self.gender = Gender(2)
        else:
            self.gender = Gender(1)

        self.boss = False
        self.type = None

        self.active = pogoinfo_data.get("active", False)
        self.team = team
        self.reward_positions = pogoinfo_data.get("lineup", {}).get("rewards", [])
        
        self.rewards = []
        for index in self.reward_positions:
            self.rewards += self.team[index]

        self.__icon = icon

    @property
    def icon_url(self):
        return self.__icon.grunt(self)

def _make_grunt_list(pogodata):
    info_grunts = httpget(INFO_URL + "active/grunts.json").json()
    pogodata.grunts = []
    enums = pogodata.get_enum("InvasionCharacter")
    for templateid, entry in pogodata.get_gamemaster(r"^CHARACTER_.*", "invasionNpcDisplaySettings"):
        id_ = enums.get(templateid, 0)

        grunt_info = info_grunts.get(str(id_), {})
        team = []
        if grunt_info:
            for i, team_position in enumerate(grunt_info.get("lineup", {}).get("team", [])):
                team.append([])
                for raw_mon in team_position:
                    team[i].append(pogodata.get_mon(template=raw_mon["template"]))

        grunt = Grunt(pogodata.icon, id_, templateid, entry, grunt_info, team)
        grunt.name = pogodata.get_locale(grunt.raw.get("trainerName", "combat_grunt_name"))

        if [t for t in grunt.template.split("_") if t in ["EXECUTIVE", "GIOVANNI"]]:
            grunt.boss = True
            
        grunt.type = pogodata.get_type(template=grunt.template.split("_")[1])

        pogodata.grunts.append(grunt)