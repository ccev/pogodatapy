import re

from .util import httpget
from .game_objects import make_type_list, make_item_list
from .moves import make_move_list
from .mons import make_mon_list, check_mons

PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/JSON/i18n_{lang}.json"

class PogoData:
    def __init__(self, language="english", icon_url=""):
        self.__cached_enums = {}
        self.icon_prefix = icon_url
        self.reload(language)

    def reload(self, language="english"):
        self.raw_protos = httpget(PROTO_URL).text
        self.raw_gamemaster = httpget(GAMEMASTER_URL).json()

        raw_locale = httpget(LOCALE_URL.format(lang=language.lower())).json()["data"]
        self.locale = {}
        for i in range(0, len(raw_locale), 2):
            self.locale[raw_locale[i]] = raw_locale[i+1]

        self.items = make_item_list(self)
        self.types = make_type_list(self)
        self.moves = make_move_list(self)

        self.mons = make_mon_list(self)
        check_mons(self)

    def __get_object(self, obj_list, args, match_one=True):
        final = []
        for obj in obj_list:
            wanted = True
            for key, value in args.items():
                if obj.__dict__.get(key) != value:
                    wanted = False
            
            if wanted:
                if match_one:
                    return obj
                final.append(obj)
        
        if not match_one:
            return final

        return None

    def get_mon(self, get_one=True, **args):
        mon = self.__get_object(self.mons, args, get_one)
        if args.get("costume", 0) > 0:
            mon = mon.copy()
            mon.costume = args["costume"]
            mon._gen_asset()

        return mon
    
    def get_type(self, **args):
        return self.__get_object(self.types, args)

    def get_item(self, **args):
        return self.__get_object(self.items, args)

    def get_move(self, **args):
        return self.__get_object(self.moves, args)

    def get_locale(self, key):
        return self.locale.get(key.lower(), "?")

    def get_enum(self, enum, reverse=False):
        cached = self.__cached_enums.get(enum.lower())
        if cached:
            return cached

        proto = re.findall(f"enum {enum} "+r"{[^}]*}", self.raw_protos, re.IGNORECASE)
        if len(proto) == 0:
            raise KeyError(f"Could not find Enum {enum}")
        
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
