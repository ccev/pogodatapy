import pickle
import re

from datetime import datetime

from enum import Enum
from .misc import httpget, PROTO_URL, GAMEMASTER_URL, LOCALE_URL, REMOTE_LOCALE_URL, INFO_URL
from .objects import Type, Move, Weather
from .pokemon import _make_mon_list, Pokemon
from .event import _make_event_list, Event
from .item import _make_item_list, Item
from .grunt import _make_grunt_list, Grunt
from .raid import _make_raid_list

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

        self.types = self.__make_simple_gameobject_list(
            "HoloPokemonType",
            "{template}",
            Type
        )
        _make_item_list(self)
        self.__make_weather_list()
        self.__make_move_list()
        _make_mon_list(self)
        _make_raid_list(self)
        _make_grunt_list(self)
        self.__make_quest_list()
        _make_event_list(self)

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
        temp_evolution
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
            if get_all:
                mon = [mon]

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

    def get_raid(self, get_all=False, **args):
        raid = self.__get_object(self.raids, args, get_all)
        if not raid:
            raid = self.__none_mon()
            raid.level = 0
        return raid

    def get_all_raids(self, **args):
        return self.get_raid(get_all=True, **args)

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

    def get_event(self, **args):
        event = self.__get_object(self.events, args)
        if not event:
            event = Event({})
        return event

    def get_locale(self, key):
        self.check_update()
        return self.locale.get(key.lower(), "?")

    def get_enum(self, enum, reverse=False, as_enum=False):
        self.check_update()
        cache_key = enum.lower()
        cached = self.__cached_enums.get(cache_key)
        if cached:
            final = cached
        else:
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

            self.__cached_enums[cache_key] = final

        if as_enum:
            return Enum(enum, final)

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

    def __make_quest_list(self):
        pass

