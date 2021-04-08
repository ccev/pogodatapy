import re
from enum import Enum
from .misc import match_enum, get_repo_content

class IconSet(Enum):
    POGO = 0
    POGO_OPTIMIZED = 1
    POGO_OUTLINE = 2
    COPYRIGHTSAFE = 10
    THEARTIFICIAL = 11
    HOME = 20
    HOME_OUTLINE = 21
    SHUFFLE = 30
    SUGMIORI_OPTIMIZED = 40
    DERP_AFD = 50
    DERP_GAMEPRESS = 51
    PIXEL_GEN3 = 60

class IconType(Enum):
    PMSF = 0
    UICON = 1
    POKEMINERS = 2

ICON_DETAILS = {
    IconSet.POGO: {
        "url": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/",
        "type": IconType.POKEMINERS
    },
    IconSet.POGO_OPTIMIZED: {
        "url": "https://raw.githubusercontent.com/whitewillem/PogoAssets/resized/no_border/",
        "type": IconType.PMSF
    }
}
class Icon:
    def __init__(self, iconset=None):
        if iconset is None:
            self.set = IconSet(0)
        else:
            self.set = match_enum(IconSet, iconset)

        self.details = ICON_DETAILS[self.set]
        self.url = self.details["url"]
        self.type = self.details["type"]

        if self.type == IconType.PMSF:
            match = re.match(r"https:\/\/raw\.githubusercontent\.com\/([^\/]*)\/([^\/]*)\/([^\/]*).*", self.url)
            user, repo, branch = match.groups()

            base_api = f"https://api.github.com/repos/{user}/{repo}/"
            sha_url = base_api + f"branches/{branch}"
            files_url = base_api + "git/trees/{sha}?recursive=true"
            icons = get_repo_content(files_url, sha_url)
            self.icons = [re.sub(r"[^\/]*\/", "", i) for i in icons]
        
    def pokemon(self, mon):
        if self.type == IconType.POKEMINERS:
            return self.url + "Images/Pokemon/" + mon.asset + ".png"
        elif self.type == IconType.PMSF:
            for monid in (mon.id, 0):
                for form in (mon.form, 0):
                    for costm in (mon.costume.value, 0):
                        if form == 0:
                            formstr = "_00"
                        else:
                            formstr = "_" + str(form)

                        if costm > 0:
                            costr = "_" + str(costm)
                        else:
                            costr = ""
    
                        icon = "pokemon_icon_" + str(monid).zfill(3) + formstr + costr + ".png"
                        if icon in self.icons:
                            return self.url + icon
    
    def item(self, item, amount=1):
        if self.type == IconType.POKEMINERS:
            url = ICON_DETAILS[IconSet.POGO_OPTIMIZED]["url"]
        elif self.type == IconType.PMSF:
            url = self.url
        return url + "rewards/reward_" + str(item.id) + "_" + str(amount) + ".png"

    def montype(self, montype):
        if self.type == IconType.POKEMINERS:
            return self.url + "Images/Types/" + montype.template + ".png"
    
    def weather(self, weather, is_day=True):
        if self.type == IconType.POKEMINERS:
            westr = weather.template.lower()
            if weather.id == 1 and is_day:
                westr = "sunny"
            elif weather.id == 2:
                westr = "rain"
            elif weather.id == 3:
                westr = "partlycloudy_"
                if is_day:
                    westr += "day"
                else:
                    westr += "night"
            elif weather.id == 4:
                westr = "cloudy"
            
            return self.url + f"Images/Weather/weatherIcon_small_{westr}.png"
