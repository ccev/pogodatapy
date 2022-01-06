import re
import copy
from .objects import GameMasterObject
from .enums import PokemonType
from .misc import httpget, INGAME_ICONS, ICON_SHA

class Pokemon(GameMasterObject):
    def __init__(self, gamemaster_entry, form_id, template):
        super().__init__(0, template, gamemaster_entry)

        self.form = form_id
        self.base_template = self.raw.get("pokemonId", "")
        #self.form_name = ""

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
            self.type = PokemonType.BASE
        else:
            self.type = PokemonType.FORM

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
        stats = self.raw.get("stats")
        if not stats:
            self.stats = []
            return
        self.stats = [stats["baseAttack"], stats["baseDefense"], stats["baseStamina"]]

def _make_mon_list(pogodata):
    def __typing(mon, type1ref, type2ref):
        typings = [mon.raw.get(type1ref), mon.raw.get(type2ref)]
        for typing in typings:
            if typing:
                mon.types.append(pogodata.get_type(template=typing))

    pogodata.mons = []
    forms = pogodata.get_enum("Form")
    megas = pogodata.get_enum("HoloTemporaryEvolutionId")
    mon_ids = pogodata.get_enum("HoloPokemonId")

    # Creating a base mon list based on GM entries
    pattern = r"^V\d{4}_POKEMON_"
    for templateid, entry in pogodata.get_gamemaster(pattern+".*", "pokemonSettings"):
        template = entry.get("form", entry.get("pokemonId"))

        if not template:
            continue

        form_id = forms.get(template, 0)
        mon = Pokemon(entry, form_id, template)
        mon.id = mon_ids.get(mon.base_template, 0)
        mon._gen_asset()

        locale_key = "pokemon_name_" + str(mon.id).zfill(4)
        mon.name = pogodata.get_locale(locale_key)

        mon.quick_moves = [pogodata.get_move(template=t) for t in mon.raw.get("quickMoves", [])]
        mon.charge_moves = [pogodata.get_move(template=t) for t in mon.raw.get("cinematicMoves", [])]

        __typing(mon, "type", "type2")

        pogodata.mons.append(mon)

        # Handling Temp (Mega) Evolutions
        for temp_evo in mon.raw.get("tempEvoOverrides", []):
            evo = mon.copy()
            evo.type = PokemonType.TEMP_EVOLUTION

            evo.temp_evolution_template = temp_evo.get("tempEvoId")
            evo.temp_evolution_id = megas.get(evo.temp_evolution_template)

            evo.raw = temp_evo
            evo.name = pogodata.get_locale(locale_key + "_" + str(evo.temp_evolution_id).zfill(4))
            evo._make_stats()

            evo.types = []
            __typing(evo, "typeOverride1", "typeOverride2")

            pogodata.mons.append(evo)
            mon.temp_evolutions.append(evo)

    # Going through GM Forms and adding missing Forms (Unown, Spinda) and making in-game assets
    form_enums = pogodata.get_enum("Form")
    for template, formsettings in pogodata.get_gamemaster(r"^FORMS_V\d{4}_POKEMON_.*", "formSettings"):
        forms = formsettings.get("forms", [])
        for form in forms:
            mon = pogodata.get_mon(template=form.get("form"))
            if not mon:
                mon = pogodata.get_mon(template=formsettings["pokemon"])
                mon = mon.copy()
                mon.type = PokemonType.FORM
                mon.template = form.get("form")
                mon.form = form_enums.get(mon.template)
                pogodata.mons.append(mon)

            asset_value = form.get("assetBundleValue")
            asset_suffix = form.get("assetBundleSuffix")
            if asset_value or asset_suffix:
                mon.asset_value = asset_value
                mon.asset_suffix = asset_suffix
            mon._gen_asset()

            """
            form_template = mon.template.replace(mon.base_template, "").strip("_")
            form_name = pogodata.get_locale("form_" + form_template)
            if form_name == "?":
                form_name = pogodata.get_locale("filter_key_" + form_template)
            if form_name == "?":
                form_name = form_template.replace("_", " ").lower()
            mon.form_name = form_name.capitalize()
            """

    # Temp Evolution assets
    evo_gm = pogodata.get_gamemaster(
        r"^TEMPORARY_EVOLUTION_V\d{4}_POKEMON_.*",
        "temporaryEvolutionSettings"
    )
    for base_template, evos in evo_gm:
        base_template = evos.get("pokemonId", "")
        evos = evos.get("temporaryEvolutions", [])
        for temp_evo_raw in evos:
            mons = pogodata.get_mon(
                get_all=True,
                base_template=base_template,
                temp_evolution_template=temp_evo_raw["temporaryEvolutionId"]
            )
            for mon in mons:
                mon.asset_value = temp_evo_raw["assetBundleValue"]
                mon._gen_asset()

    # Making Pokemon.evolutions attributes
    def append_evolution(mon, to_append):
        evolutions = mon.raw.get("evolutionBranch", [])
        for evo_raw in evolutions:
            if "temporaryEvolution" in evo_raw:
                continue
            template = evo_raw.get("form", evo_raw.get("evolution"))
            if not template:
                continue
            evo = pogodata.get_mon(
                template=template
            )
            to_append.append(evo)
            append_evolution(evo, to_append)
    for mon in pogodata.mons:
        evos = []
        append_evolution(mon, evos)
        mon.evolutions = evos

    master = httpget(ICON_SHA).json()
    sha = master["commit"]["sha"]
    icons = httpget(INGAME_ICONS.format(sha=sha)).json()["tree"]
    icons = [i["path"] for i in icons]

    for icon in icons:
        match = re.match(r"Images/Pokemon/pokemon_icon(_\d*){3}(?!\d*_?shiny).png", icon)
        if match:
            icon = icon.replace(".png", "")
            icon = icon.replace("Images/Pokemon/", "")

            costume = re.findall(r"_\d*$", icon)[0]
            og_asset = re.sub(costume + "$", "", icon)
            og_asset = re.sub(r"_01$", "_00", og_asset)
            costume = int(costume.strip("_"))

            mon = pogodata.get_mon(asset=og_asset)
            copy = mon.copy()
            copy.costume = costume
            copy._gen_asset()
            pogodata.mons.append(copy)
