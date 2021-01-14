from pogodata.pogodata import PogoData
from pogodata.util import httpget
from pogodata.pogoinfo.raids import Raids
from pogodata.pogoinfo.full_grunts import FullGrunt

INFO_URL = "https://raw.githubusercontent.com/ccev/pogoinfo/v2/"

class PogoInfo:
    def __init__(self, pogodata=None):
        if pogodata:
            self.pogodata = pogodata
        else:
            self.pogodata = PogoData()

        self.reload()
    
    def reload(self):
        self.__make_raids()
        self.__make_grunts()

    def __make_raids(self):
        self.raids = Raids()
        raw_raids = httpget(INFO_URL + "active/raids.json").json()
        for level, mons in raw_raids.items():
            for raw_mon in mons:
                if not raw_mon:
                    continue
                if "evolution" in raw_mon:
                    base_mon = self.pogodata.get_mon(
                        id=raw_mon.get("id"),
                        form=raw_mon.get("form"),
                        costume=raw_mon.get("costume")
                    )
                    for evo in base_mon.temp_evolutions:
                        if evo.id == raw_mon.get("evolution"):
                            mon = evo
                            break
                else:
                    mon = self.pogodata.get_mon(
                        template=raw_mon.get("template"),
                        costume=raw_mon.get("costume", 0)
                    )

                if mon:
                    self.raids.add_mon(level, mon)
        
    def __make_grunts(self):
        self.grunts = []
        raw_grunts = httpget(INFO_URL + "active/grunts.json").json()
        for data in raw_grunts.values():
            grunt = FullGrunt(data)
            grunt.character = self.pogodata.get_grunt(template=data["character"]["template"])
            for i, team_position in enumerate(data.get("lineup", {}).get("team", [])):
                grunt.team.append([])
                for raw_mon in team_position:
                    grunt.team[i].append(self.pogodata.get_mon(template=raw_mon["template"]))
            self.grunts.append(grunt)
