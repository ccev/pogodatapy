import pickle
import re

from datetime import datetime

from enum import Enum
from .misc import httpget, PROTO_URL, GAMEMASTER_URL, LOCALE_URL, INFO_URL
from .objects import Pokemon, Type, Item, Move, Raids, Grunt, Weather
from .enums import PokemonType

def load_pogodata(path="", name="__pogodata_save__"):
    with open(f"{path}{name}.pickle", "rb") as handle:
        return(pickle.load(handle))

class PogoData:
    """The class holding all data this module provides

    Parameters
    ----------
    language: :class:`str`
        The language used for translations. Default: english
        Available languages: https://github.com/PokeMiners/pogo_assets/tree/master/Texts/Latest%20APK/JSON
    icon_url: :class:`str`
        An URL to the base of an UIcons-compatible icon repo for UIcon support.

    Attributes
    ----------
    mons: List[:class:`.Pokemon`]
        All Pokémon.
    items: List[:class:`.items.Item`]
        All Items.
    types: List[:class:`.types.Type`]
        All available Pokémon Types.
    moves: List[:class:`.moves.Move`]
        All Moves.
    grunts: List[:class:`.grunts.Grunt`]
        All Grunts.
    """
    def __init__(self, language="english", update_interval=24, icon_url=""):
        self.__make_locale_url(language)
        self.update_interval = update_interval
        self.icon_url = icon_url
        self.reload()

    def __make_locale_url(self, language):
        self.__locale_url = LOCALE_URL.format(lang=language.lower())

    def reload(self, language=None):
        """Reloads all data, as if you'd re-initialize the class.

        Parameters
        ----------
        language: :class:`str`
            The language used for translations. Default: english
            Available languages: https://github.com/PokeMiners/pogo_assets/tree/master/Texts/Latest%20APK/JSON
        """
        self.__cached_enums = {}
        if language:
            self.__make_locale_url(language)

        self.raw_protos = httpget(PROTO_URL).text
        self.raw_gamemaster = httpget(GAMEMASTER_URL).json()

        raw_locale = httpget(self.__locale_url).json()["data"]
        self.locale = {}
        for i in range(0, len(raw_locale), 2):
            self.locale[raw_locale[i]] = raw_locale[i+1]

        self.updated = datetime.utcnow()

        self.items = self.__make_simple_gameobject_list(
            "Item",
            "{template}_name",
            Item
        )
        self.types = self.__make_simple_gameobject_list(
            "HoloPokemonType",
            "{template}",
            Type
        )
        self.__make_weather_list()
        self.__make_move_list()
        self.__make_mon_list()
        self.__make_raid_list()
        self.__make_grunt_list()
        self.__make_quest_list()

    def check_update(self):
        if not self.update_interval:
            return
        
        if (datetime.utcnow() - self.updated).seconds // 3600 >= self.update_interval:
            self.reload()

    def save(self, path="", name="__pogodata_save__"):
        with open(f"{path}{name}.pickle", "wb") as handle:
            pickle.dump(self, handle)

    def __make_simple_gameobject_list(self, enum, locale_key, obj):
        objs = []
        for template, id_ in self.get_enum(enum).items():
            obj_ = obj(id_, template)
            obj_.name = self.get_locale(locale_key.format(template=template))
            objs.append(obj_)
        return objs

    def __get_object(self, obj_list, args, match_all=False):
        self.check_update()

        final = []
        for obj in obj_list:
            wanted = True
            for key, value in args.items():
                big_value = obj.__dict__.get(key)

                if isinstance(big_value, list):
                    if not set(value).issubset(set(big_value)):
                        wanted = False
                elif isinstance(big_value, Enum):
                    if not ((big_value.value == value) or (big_value.name == value) or (big_value == value)):
                        wanted = False
                elif big_value != value:
                    wanted = False

            if wanted:
                if not match_all:
                    return obj
                final.append(obj)

        if match_all:
            return final

        return None

    def get_mon(self, get_all=False, **args):
        """Find a Pokémon that matches every parameter given.

        Parameters
        ----------
        get_all: :class:`bool`
            If False, return the first matching Pokémon. If True, return all matching Pokémon.
            Defaults to False.
        id: :class:`int`
        template: :class:`str`
        type: `BASE`, `FORM` or `TEMP_EVOLUTION`
        form: 
        base_template
        costume
        asset
        temp_evolution_id
        temp_evolution_template
        types
        qick_moves
        charge_moves
        evolutions
        temp_evolutions



        Returns
        -------
        """
        mon = self.__get_object(self.mons, args, get_all)
        if args.get("costume", 0) > 0:
            mon = mon.copy()
            mon.costume = args["costume"]
            mon._gen_asset()

        return mon

    def get_default_mon(self, **args):
        args["form"] = 0
        mon = self.__get_object(self.mons, args)
        if not mon:
            return None
        normal_mon = self.__get_object(self.mons, {"template": mon.base_template + "_NORMAL"})
        if normal_mon:
            mon = normal_mon
        return mon

    def get_type(self, **args):
        if "template" in args:
            if not args["template"].startswith("POKEMON_TYPE_"):
                args["template"] = "POKEMON_TYPE_" + args["template"]
        return self.__get_object(self.types, args)

    def get_item(self, **args):
        return self.__get_object(self.items, args)

    def get_move(self, **args):
        return self.__get_object(self.moves, args)

    def get_weather(self, **args):
        return self.__get_object(self.weather, args)

    def get_grunt(self, **args):
        return self.__get_object(self.grunts, args)

    def get_locale(self, key):
        self.check_update()
        return self.locale.get(key.lower(), "?")

    def get_enum(self, enum, reverse=False):
        self.check_update()
        cached = self.__cached_enums.get(enum.lower())
        if cached:
            return cached

        proto = re.findall(f"enum {enum} "+r"{[^}]*}", self.raw_protos, re.IGNORECASE)
        if len(proto) == 0:
            return {}

        proto = proto[0].replace("\t", "")

        final = {}
        proto = proto.split("{\n")[1].split("\n}")[0]
        for entry in proto.split("\n"):
            k = entry.split(" =")[0]
            v = int(entry.split("= ")[1].split(";")[0])
            final[k] = v

        self.__cached_enums[enum.lower()] = final

        if reverse:
            final = {value:key for key, value in final.items()}

        return final

    def get_gamemaster(self, pattern, settings=None):
        self.check_update()
        result = []
        for entry in self.raw_gamemaster:
            templateid = entry.get("templateId", "")
            if re.search(pattern, templateid):
                data = entry.get("data", {})
                if settings:
                    data = data.get(settings, {})

                result.append((
                    templateid, data
                ))
        return result

    # Build lists

    def __make_weather_list(self):
        self.weather = []
        wather_enum = self.get_enum("WeatherCondition")
        for _, entry in self.get_gamemaster(r"^WEATHER_AFFINITY_.*", "weatherAffinities"):
            template = entry["weatherCondition"]
            weather = Weather(template, entry, wather_enum.get(template))
            weather.name = self.get_locale("weather_" + template)
            for boost_type in entry["pokemonType"]:
                type_ = self.get_type(template=boost_type)
                weather.type_boosts.append(type_)
            self.weather.append(weather)

    def __make_move_list(self):
        self.moves = []
        move_enum = self.get_enum("HoloPokemonMove")
        pattern = r"^COMBAT_V\d{4}_MOVE_"
        for templateid, entry in self.get_gamemaster(pattern+".*", "combatMove"):
            template = re.sub(pattern, "", templateid)
            move_id = move_enum.get(template, 0)
            move = Move(template, entry, move_id)
            move.type = self.get_type(template=move.raw.get("type"))
            move.name = self.get_locale("move_name_" + str(move.id).zfill(4))
            self.moves.append(move)

    def __make_raid_list(self):
        self.raids = Raids()
        raw_raids = httpget(INFO_URL + "active/raids.json").json()
        for level, mons in raw_raids.items():
            for raw_mon in mons:
                if not raw_mon:
                    continue
                if "evolution" in raw_mon:
                    base_mon = self.get_mon(
                        id=raw_mon.get("id"),
                        form=raw_mon.get("form"),
                        costume=raw_mon.get("costume")
                    )
                    for evo in base_mon.temp_evolutions:
                        if evo.id == raw_mon.get("evolution"):
                            mon = evo
                            break
                else:
                    mon = self.get_mon(
                        template=raw_mon.get("template"),
                        costume=raw_mon.get("costume", 0)
                    )

                if mon:
                    self.raids.add_mon(level, mon)

    def __make_grunt_list(self):
        info_grunts = httpget(INFO_URL + "active/grunts.json").json()
        self.grunts = []
        enums = self.get_enum("InvasionCharacter")
        for templateid, entry in self.get_gamemaster(r"^CHARACTER_.*", "invasionNpcDisplaySettings"):
            id_ = enums.get(templateid, 0)

            grunt_info = info_grunts.get(str(id_))
            team = []
            if grunt_info:
                for i, team_position in enumerate(grunt_info.get("lineup", {}).get("team", [])):
                    team.append([])
                    for raw_mon in team_position:
                        team[i].append(self.get_mon(template=raw_mon["template"]))

            grunt = Grunt(id_, templateid, entry, grunt_info, team)
            grunt.name = self.get_locale(grunt.raw.get("trainerName", "combat_grunt_name"))

            if [t for t in grunt.template.split("_") if t in ["EXECUTIVE", "GIOVANNI"]]:
                grunt.boss = True
                
            grunt.type = self.get_type(template=grunt.template.split("_")[1])

            self.grunts.append(grunt)

    def __make_quest_list(self):
        pass


    def __make_mon_list(self):
        def __typing(mon, type1ref, type2ref):
            typings = [mon.raw.get(type1ref), mon.raw.get(type2ref)]
            for typing in typings:
                if typing:
                    mon.types.append(self.get_type(template=typing))

        self.mons = []
        forms = self.get_enum("Form")
        megas = self.get_enum("HoloTemporaryEvolutionId")
        mon_ids = self.get_enum("HoloPokemonId")

        # Creating a base mon list based on GM entries
        pattern = r"^V\d{4}_POKEMON_"
        for templateid, entry in self.get_gamemaster(pattern+".*", "pokemonSettings"):
            template = re.sub(pattern, "", templateid)
            form_id = forms.get(template, 0)
            mon = Pokemon(entry, form_id, template)
            mon.id = mon_ids.get(mon.base_template, 0)
            mon._gen_asset()

            locale_key = "pokemon_name_" + str(mon.id).zfill(4)
            mon.name = self.get_locale(locale_key)

            mon.quick_moves = [self.get_move(template=t) for t in mon.raw.get("quickMoves", [])]
            mon.charge_moves = [self.get_move(template=t) for t in mon.raw.get("cinematicMoves", [])]

            __typing(mon, "type", "type2")

            self.mons.append(mon)

            # Handling Temp (Mega) Evolutions
            for temp_evo in mon.raw.get("tempEvoOverrides", []):
                evo = mon.copy()
                evo.type = PokemonType.TEMP_EVOLUTION

                evo.temp_evolution_template = temp_evo.get("tempEvoId")
                evo.temp_evolution_id = megas.get(evo.temp_evolution_template)

                evo.raw = temp_evo
                evo.name = self.get_locale(locale_key + "_" + str(evo.temp_evolution_id).zfill(4))
                evo._make_stats()

                evo.types = []
                __typing(evo, "typeOverride1", "typeOverride2")

                self.mons.append(evo)
                mon.temp_evolutions.append(evo)

        # Going through GM Forms and adding missing Forms (Unown, Spinda) and making in-game assets
        form_enums = self.get_enum("Form")
        for template, formsettings in self.get_gamemaster(r"^FORMS_V\d{4}_POKEMON_.*", "formSettings"):
            forms = formsettings.get("forms", [])
            for form in forms:
                mon = self.get_mon(template=form.get("form"))
                if not mon:
                    mon = self.get_mon(template=formsettings["pokemon"])
                    mon = mon.copy()
                    mon.type = PokemonType.FORM
                    mon.template = form.get("form")
                    mon.form = form_enums.get(mon.template)
                    self.mons.append(mon) 

                asset_value = form.get("assetBundleValue")
                asset_suffix = form.get("assetBundleSuffix")
                if asset_value or asset_suffix:
                    mon.asset_value = asset_value
                    mon.asset_suffix = asset_suffix
                mon._gen_asset()

        # Temp Evolution assets
        evo_gm = self.get_gamemaster(
            r"^TEMPORARY_EVOLUTION_V\d{4}_POKEMON_.*",
            "temporaryEvolutionSettings"
        )
        for base_template, evos in evo_gm:
            base_template = evos.get("pokemonId", "")
            evos = evos.get("temporaryEvolutions", [])
            for temp_evo_raw in evos:
                mon = self.get_mon(
                    base_template=base_template,
                    temp_evolution_template=temp_evo_raw["temporaryEvolutionId"]
                )
                mon.asset_value = temp_evo_raw["assetBundleValue"]
                mon._gen_asset()

        # Making Pokemon.evolutions attributes
        for mon in self.mons:
            evolutions = mon.raw.get("evolutionBranch", [])
            for evo_raw in evolutions:
                if "temporaryEvolution" in evo_raw:
                    continue
                evo = self.get_mon(
                    template=evo_raw.get("form", evo_raw["evolution"])
                )
                mon.evolutions.append(evo)
