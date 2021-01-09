import re
import copy

from .util import httpget
from .game_objects import make_type_list, make_item_list
from .moves import make_move_list
from .mons import make_mon_list

PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/JSON/i18n_{lang}.json"

class PogoData:
    def __init__(self, language="english"):
        self.__cached_enums = {}
        self.reload(language)

    def reload(self, language):
        self.raw_protos = httpget(PROTO_URL).text
        self.raw_gamemaster = httpget(GAMEMASTER_URL).json()

        raw_locale = httpget(LOCALE_URL.format(lang=language)).json()["data"]
        self.locale = {}
        for i in range(0, len(raw_locale), 2):
            self.locale[raw_locale[i]] = raw_locale[i+1]

        self.items = make_item_list(self)
        self.types = make_type_list(self)
        self.moves = make_move_list(self)

        self.mons = make_mon_list(self)[::-1]

        form_enums = self.get_enum("Form")
        for entry in self.raw_gamemaster:
            if re.search(r"^FORMS_V\d{4}_POKEMON_.*", entry.get("templateId", "")):
                formsettings = entry.get("data").get("formSettings")
                forms = formsettings.get("forms", [])
                for form in forms:
                    mon = self.get_mon(template=form.get("form"))
                    if not mon:
                        mon = self.get_mon(template=formsettings["pokemon"])
                        mon = copy.copy(mon)
                        mon.template = form.get("form")
                        mon.form = form_enums.get(mon.template)
                        self.mons.append(mon) 

                    asset_value = form.get("assetBundleValue")
                    asset_suffix = form.get("assetBundleSuffix")
                    if asset_value or asset_suffix:
                        mon.asset_value = asset_value
                        mon.asset_suffix = asset_suffix
                        mon._gen_asset()

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
        return self.__get_object(self.mons, args, get_one)
    
    def get_type(self, **args):
        return self.__get_object(self.types, args)

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
    
    #@property
