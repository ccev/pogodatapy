import re
import copy
from .game_objects import GameObject, GameMasterObject
from .util import gen_uicon

TYPES = ["BASE", "FORM", "TEMP_EVOLUTION"]

class TempEvolution(GameObject):
    def __init__(self, temp_raw):
        super().__init__(0, temp_raw.get("tempEvoId"))
        self.raw = temp_raw
        self.stats = [v for v in self.raw.get("stats", {}).values()]
        self.types = []

class Pokemon(GameMasterObject):
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
        self._make_stats()

        self.costume = 0

        self.asset_value = None
        self.asset_suffix = None
        self._gen_asset()

        self.temp_evolution_id = 0
        self.temp_evolution_template = ""

        if self.template == self.base_template:
            self.type = TYPES[0]
        else:
            self.type = TYPES[1]

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
            mon = Pokemon(entry, form_id, template)

            locale_key = "pokemon_name_" + str(mon.id).zfill(4)
            mon.name = pogodata.get_locale(locale_key)

            mon.quick_moves = [pogodata.get_move(template=t) for t in mon.raw.get("quickMoves", [])]
            mon.charge_moves = [pogodata.get_move(template=t) for t in mon.raw.get("cinematicMoves", [])]

            __typing(mon, "type", "type2")

            mons.append(mon)

            for temp_evo in mon.raw.get("tempEvoOverrides", []):
                evo = mon.copy()
                evo.type = TYPES[2]

                evo.temp_evolution_template = temp_evo.get("tempEvoId")
                evo.temp_evolution_id = megas.get(evo.temp_evolution_template)

                evo.raw = temp_evo
                evo.name = pogodata.get_locale(locale_key + "_" + str(evo.temp_evolution_id).zfill(4))
                evo._make_stats()

                evo.types = []
                __typing(evo, "typeOverride1", "typeOverride2")

                mons.append(evo)
                mon.temp_evolutions.append(evo)

    return mons

def check_mons(pogodata):
    form_enums = pogodata.get_enum("Form")
    for entry in pogodata.raw_gamemaster:
        template = entry.get("templateId", "")
        if re.search(r"^FORMS_V\d{4}_POKEMON_.*", template):
            formsettings = entry.get("data").get("formSettings")
            forms = formsettings.get("forms", [])
            for form in forms:
                mon = pogodata.get_mon(template=form.get("form"))
                if not mon:
                    mon = pogodata.get_mon(template=formsettings["pokemon"])
                    mon = mon.copy()
                    mon.type = TYPES[1]
                    mon.template = form.get("form")
                    mon.form = form_enums.get(mon.template)
                    pogodata.mons.append(mon) 

                asset_value = form.get("assetBundleValue")
                asset_suffix = form.get("assetBundleSuffix")
                if asset_value or asset_suffix:
                    mon.asset_value = asset_value
                    mon.asset_suffix = asset_suffix
                    mon._gen_asset()

        if re.search(r"^TEMPORARY_EVOLUTION_V\d{4}_POKEMON_.*", template):
            evos = entry.get("data", {}).get("temporaryEvolutionSettings", {})
            base_template = evos.get("pokemonId", "")
            evos = evos.get("temporaryEvolutions", [])
            for temp_evo_raw in evos:
                mon = pogodata.get_mon(
                    base_template=base_template,
                    temp_evolution_template=temp_evo_raw["temporaryEvolutionId"]
                )
                mon.asset_value = temp_evo_raw["assetBundleValue"]
                mon._gen_asset()

    for mon in pogodata.mons:
        evolutions = mon.raw.get("evolutionBranch", [])
        for evo_raw in evolutions:
            if "temporaryEvolution" in evo_raw:
                continue
            evo = pogodata.get_mon(
                template=evo_raw.get("form", evo_raw["evolution"])
            )
            mon.evolutions.append(evo)