import pickle
import re

from datetime import datetime

from enum import Enum
from .misc import httpget, PROTO_URL, GAMEMASTER_URL, LOCALE_URL, REMOTE_LOCALE_URL, INFO_URL
from .objects import Type, Item, Move, Raids, Grunt, Weather
from .enums import PokemonType
from .pokemon import _make_mon_list, Pokemon

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
        lang = language.lower().capitalize()
        self.__locale_url = LOCALE_URL.format(lang=lang)
        self.__remote_locale_url = REMOTE_LOCALE_URL.format(lang=lang)

    def __make_locale(self, url):
        raw = httpget(url).text
        keys = re.findall(r"(?<=RESOURCE ID: ).*", raw)
        values = re.findall(r"(?<=TEXT: ).*", raw)

        return {keys[i].strip("\r"): values[i].strip("\r") for i in range(len(keys))}

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

        apk_locale = self.__make_locale(self.__locale_url)
        remote_locale = self.__make_locale(self.__remote_locale_url)
        self.locale = {**apk_locale, **remote_locale}

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
        _make_mon_list(self)
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

    def __none_mon(self):
        return Pokemon({}, 0, "UNSET")

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

        if not mon:
            mon = self.__none_mon()

        return mon

    def get_default_mon(self, **args):
        mons = self.get_mon(get_all=True, **args)
        if not mons:
            return self.__none_mon()
        for mon in mons:
            if "_NORMAL" in mon.template:
                return mon
        return mons[0]

    def get_all_mons(self, **args):
        return self.get_mon(get_all=True, **args)

    def get_type(self, **args):
        if "template" in args:
            if not args["template"].startswith("POKEMON_TYPE_"):
                args["template"] = "POKEMON_TYPE_" + args["template"]

        type_ = self.__get_object(self.types, args)
        if not type_:
            type_ = Type(0, "UNSET")
        return type_

    def get_item(self, **args):
        item = self.__get_object(self.items, args)
        if not item:
            item = Item(0, "UNSET")
        return item

    def get_move(self, **args):
        move = self.__get_object(self.moves, args)
        if not move:
            move = Move("UNSET", {}, 0)
        return move

    def get_weather(self, **args):
        weather = self.__get_object(self.weather, args)
        if not weather:
            weather = Weather("UNSET", {}, 0)
        return weather

    def get_grunt(self, **args):
        grunt = self.__get_object(self.grunts, args)
        if not grunt:
            grunt = Grunt(0, "UNSET", {}, {}, [])
        return grunt

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
            if "}" in entry or "{" in entry:
                continue
            k = entry.split(" =")[0].strip()
            v = int(entry.split("= ")[1].split(";")[0].strip())
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
                mon = self.get_mon(**raw_mon)

                if mon:
                    self.raids.add_mon(level, mon)

    def __make_grunt_list(self):
        info_grunts = httpget(INFO_URL + "active/grunts.json").json()
        self.grunts = []
        enums = self.get_enum("InvasionCharacter")
        for templateid, entry in self.get_gamemaster(r"^CHARACTER_.*", "invasionNpcDisplaySettings"):
            id_ = enums.get(templateid, 0)

            grunt_info = info_grunts.get(str(id_), {})
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

    def __make_event_list(self):
        raw_events = httpget(INFO_URL + "active/events.json").json()
        self.events = []

