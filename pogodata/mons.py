import re
import copy
from .game_objects import GameObject, GameMasterObject
from .util import gen_uicon

class TempEvolution(GameObject):
    def __init__(self, temp_raw):
        super().__init__(0, temp_raw.get("tempEvoId"))
        self.raw = temp_raw
        self.stats = [v for v in self.raw.get("stats", {}).values()]
        self.types = []

class Mon(GameMasterObject):
    def __init__(self, gamemaster_entry, form_id, template):
        super().__init__(
            int(gamemaster_entry["templateId"].split("V")[1].split("_")[0]),
            template,
            gamemaster_entry,
            "pokemonSettings"
        )

        self.form = form_id
        self.base_template = self.raw.get("pokemonId", "")

        self.quick_moves = []
        self.charge_moves = []
        self.types = []
        self.evolutions = []
        self.temp_evolutions = []
        self.stats = [v for v in self.raw.get("stats", {}).values()]

        self.costume = 0

        self.asset_value = None
        self.asset_suffix = None
        self._gen_asset()

    def copy(self):
        return copy.copy(self)

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

def make_mon_list(pogodata):
    def __typing(mon, type1ref, type2ref):
        typings = [mon.raw.get(type1ref), mon.raw.get(type2ref)]
        for typing in typings:
            if typing:
                mon.types.append(pogodata.get_type(template=typing))

    mons = []
    forms = pogodata.get_enum("Form")
    megas = pogodata.get_enum("HoloTemporaryEvolutionId")
    for entry in pogodata.raw_gamemaster:
        templateid = entry["templateId"]
        if re.search(r"^V\d{4}_POKEMON_.*", templateid):
            template = re.sub(r"^V\d{4}_POKEMON_", "", templateid)
            form_id = forms.get(template, 0)
            mon = Mon(entry, form_id, template)

            locale_key = "pokemon_name_" + str(mon.id).zfill(4)
            mon.name = pogodata.get_locale(locale_key)

            mon.quick_moves = [pogodata.get_move(template=t) for t in mon.raw.get("quickMoves", [])]
            mon.charge_moves = [pogodata.get_move(template=t) for t in mon.raw.get("cinematicMoves", [])]

            __typing(mon, "type", "type2")

            for temp_evo in mon.raw.get("tempEvoOverrides", []):
                evo = TempEvolution(temp_evo)
                evo.id = megas.get(evo.template)
                evo.name = pogodata.get_locale(locale_key + "_" + str(evo.id).zfill(4))
                
                __typing(evo, "typeOverride1", "typeOverride2")

                mon.temp_evolutions.append(evo)
                
            mons.append(mon)

    return mons

def check_mons(pogoinfo):
    form_enums = pogoinfo.get_enum("Form")
    for entry in pogoinfo.raw_gamemaster:
        if re.search(r"^FORMS_V\d{4}_POKEMON_.*", entry.get("templateId", "")):
            formsettings = entry.get("data").get("formSettings")
            forms = formsettings.get("forms", [])
            for form in forms:
                mon = pogoinfo.get_mon(template=form.get("form"))
                if not mon:
                    mon = pogoinfo.get_mon(template=formsettings["pokemon"])
                    mon = mon.copy()
                    mon.template = form.get("form")
                    mon.form = form_enums.get(mon.template)
                    pogoinfo.mons.append(mon) 

                asset_value = form.get("assetBundleValue")
                asset_suffix = form.get("assetBundleSuffix")
                if asset_value or asset_suffix:
                    mon.asset_value = asset_value
                    mon.asset_suffix = asset_suffix
                    mon._gen_asset()

    for mon in pogoinfo.mons:
        evolutions = mon.raw.get("evolutionBranch", [])
        for evo_raw in evolutions:
            if "temporaryEvolution" in evo_raw:
                continue
            evo = pogoinfo.get_mon(
                template=evo_raw.get("form", evo_raw["evolution"])
            )
            mon.evolutions.append(evo)