import requests
from datetime import datetime

INFO_URL = "https://raw.githubusercontent.com/ccev/pogoinfo/v2/"
PROTO_URL = "https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto"
GAMEMASTER_URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/JSON/i18n_{lang}.json"

def httpget(url):
    return requests.get(url)

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
