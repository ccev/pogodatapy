import requests
import time
from datetime import datetime

INFO_URL = "https://raw.githubusercontent.com/ccev/pogoinfo/v2/"
PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/vbase.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/{lang}.txt"
REMOTE_LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20Remote/{lang}.txt"
INGAME_ICONS = "https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/{sha}?recursive=true"
ICON_SHA = "https://api.github.com/repos/PokeMiners/pogo_assets/branches/master"

"""
HARDCODED_FORM_NAMES = {
    "SHOCK": "shock_drive",
	"BURN": "burn_drive",
	"CHILL": "chill_drive",
	"DOUSE": "douse_drive",
    "PLANT": "plant_coak",
    "SANDY": "sandy_coak",
    "TRASH": "trash_coak",
    "SUNNY": "sun",
    "RAINY": "rain",
    "SNOWY": "snow",
    "STANDARD": "standard_mode",
    "ZEN": "zen_mode",

}
"""

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
