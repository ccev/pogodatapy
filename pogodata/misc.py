import requests
import time
from enum import Enum
from datetime import datetime

INFO_URL = "https://raw.githubusercontent.com/ccev/pogoinfo/v2/"
PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/vbase.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/{lang}.txt"
REMOTE_LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20Remote/{lang}.txt"

INGAME_ICONS = "https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/{sha}?recursive=true"
ICON_SHA = "https://api.github.com/repos/PokeMiners/pogo_assets/branches/master"


def httpget(url):
    result = None
    while not result:
        try:
            result = requests.get(url)
        except Exception:
            pass
        if not result:
            time.sleep(60)
    return result


def get_commit_date(url, branch="master"):
    splits = url.split(f"/{branch}/")
    repo = splits[0].split("content.com/")[1]
    path = splits[1]
    commit_api_url = f"https://api.github.com/repos/{repo}/commits?path={path}&page=1&per_page=1"
    date = httpget(commit_api_url).json()[0]["commit"]["author"]["date"]
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")


def gen_uicon(**args):
    icon = ""
    for key, value in args.items():
        if value > 0:
            icon += key + str(value)
    return icon + ".png"


def match_enum(enum, value):
    try:
        type_ = enum[value.upper()]
    except Exception as e:
        try:
            type_ = enum(value)
        except Exception :
            type_ = enum(0)
    
    return type_


def get_repo_content(repo_url, sha_url):
    master = httpget(sha_url).json()
    sha = master["commit"]["sha"]
    new_url = repo_url.format(sha=sha)
    icons = httpget(new_url).json()["tree"]
    icons = [i["path"] for i in icons]
    return icons


CP_MULTIPLIERS = {
    1: 0.0939999967813492,
    2: 0.166397869586945,
    3: 0.215732470154762,
    4: 0.255720049142838,
    5: 0.290249884128571,
    6: 0.321087598800659,
    7: 0.349212676286697,
    8: 0.375235587358475,
    9: 0.399567276239395,
    10: 0.422500014305115,
    11: 0.443107545375824,
    12: 0.46279838681221,
    13: 0.481684952974319,
    14: 0.499858438968658,
    15: 0.517393946647644,
    16: 0.534354329109192,
    17: 0.550792694091797,
    18: 0.566754519939423,
    19: 0.582278907299042,
    20: 0.597400009632111,
    21: 0.61215728521347,
    22: 0.626567125320435,
    23: 0.6406529545784,
    24: 0.654435634613037,
    25: 0.667934000492096,
    26: 0.681164920330048,
    27: 0.694143652915955,
    28: 0.706884205341339,
    29: 0.719399094581604,
    30: 0.731700003147125,
    31: 0.737769484519958,
    32: 0.743789434432983,
    33: 0.749761044979095,
    34: 0.75568550825119,
    35: 0.761563837528229,
    36: 0.767397165298462,
    37: 0.773186504840851,
    38: 0.778932750225067,
    39: 0.784636974334717,
    1.5: 0.135137432089339,
    2.5: 0.192650913155325,
    3.5: 0.236572651424822,
    4.5: 0.273530372106572,
    5.5: 0.306057381389863,
    6.5: 0.335445031996451,
    7.5: 0.362457736609939,
    8.5: 0.387592407713878,
    9.5: 0.4111935532161,
    10.5: 0.432926420512509,
    11.5: 0.453059948165049,
    12.5: 0.472336085311278,
    13.5: 0.490855807179549,
    14.5: 0.5087017489616,
    15.5: 0.525942516110322,
    16.5: 0.542635753803599,
    17.5: 0.558830584490385,
    18.5: 0.57456912814537,
    19.5: 0.589887907888945,
    20.5: 0.604823648665171,
    21.5: 0.619404107958234,
    22.5: 0.633649178748576,
    23.5: 0.647580971386554,
    24.5: 0.661219265805859,
    25.5: 0.674581885647492,
    26.5: 0.687684901255373,
    27.5: 0.700542901033063,
    28.5: 0.713169074873823,
    29.5: 0.725575586915154,
    30.5: 0.734741038550429,
    31.5: 0.740785579737136,
    32.5: 0.746781197247765,
    33.5: 0.752729099732281,
    34.5: 0.758630370209851,
    35.5: 0.76448604959218,
    36.5: 0.770297293677362,
    37.5: 0.776064947064992,
    38.5: 0.781790050767666,
    39.5: 0.787473608513275,
    40: 0.790300011634826,
    40.5: 0.792803950958807,
    41: 0.795300006866455,
    41.5: 0.797803921486970,
    42: 0.800300002098083,
    42.5: 0.802803892322847,
    43: 0.805299997329711,
    43.5: 0.807803863460723,
    44: 0.810299992561340,
    44.5: 0.812803834895026,
    45: 0.815299987792968,
    45.5: 0.817803806620319,
    46: 0.820299983024597,
    46.5: 0.822803778631297,
    47: 0.825299978256225,
    47.5: 0.827803750922782,
    48: 0.830299973487854,
    48.5: 0.832803753381377,
    49: 0.835300028324127,
    49.5: 0.837803755931569,
    50: 0.840300023555755,
    50.5: 0.842803729034748,
    51: 0.845300018787384,
    51.5: 0.847803702398935,
    52: 0.850300014019012,
    52.5: 0.852803676019539,
    53: 0.855300009250640,
    53.5: 0.857803649892077,
    54: 0.860300004482269,
    54.5: 0.862803624012168,
    55: 0.865299999713897
}
