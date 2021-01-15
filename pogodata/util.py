import requests

POKEMON_TYPES = ["BASE", "FORM", "TEMP_EVOLUTION"]

INFO_URL = "https://raw.githubusercontent.com/ccev/pogoinfo/v2/"
PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/JSON/i18n_{lang}.json"

def httpget(url):
    return requests.get(url)

def gen_uicon(**args):
    icon = ""
    for key, value in args.items():
        if value > 0:
            icon += key + str(value)
    return icon + ".png"
