from enum import Enum
from datetime import datetime
from .misc import match_enum, httpget, INFO_URL

class EventType(Enum):
    UNKNOWN = 0
    EVENT = 1
    COMMUNITY_DAY = 2
    SPOTLIGHT_HOUR = 3
    RAID_HOUR = 4

class EventBonusType(Enum):
    UNKNOWN = 0
    HATCH = "reduced-hatch-distance"
    STARDUST = "increased-stardust"
    CANDY = "increased-candy"
    XP = "increased-xp"
    TRADE_RANGE = "increased-trade-range"
    LUCKY = "increased-lucky-chance"
    INCENSE = "longer-incense"
    LUCKY_EGG = "longer-lucky-egg"
    STAR_PIECE = "longer-star-piece"

class EventBonus:
    def __init__(self, bonus):
        self.text = bonus.get("text", "")
        self.type = match_enum(EventBonusType, bonus.get("template", 0))
        self.value = bonus.get("value", 0)

class Event:
    def __init__(self, event):
        self.name = event.get("name", "?")
        self.type = match_enum(EventType, event["type"])
        self.start = self.__str_to_datetime(event.get("start"))
        self.end = self.__str_to_datetime(event.get("end"))

        self.spawns = []
        self.eggs = []
        self.raids = []
        self.shinies = []

        self.bonuses = [EventBonus(b) for b in event.get("bonuses", [])]
        self.features = event.get("features", [])

        self.has_quests = event.get("has_quests", False)
        self.has_spawnpoints = event.get("has_spawnpoints", False)

    def __str_to_datetime(self, time):
        if time is None:
            return None
        return datetime.strptime(time, "%Y-%m-%d %H:%M")

def __mon_list(raw_list, get_mon):
    final = []
    for raw_mon in raw_list:
        mon = get_mon(**raw_mon)
        final.append(mon)
    return final

def _make_event_list(pogodata):
    raw_events = httpget(INFO_URL + "active/events.json").json()
    pogodata.events = []

    for raw_event in raw_events:
        event = Event(raw_event)
        event.spawns = __mon_list(raw_event["spawns"], pogodata.get_mon)
        event.eggs = __mon_list(raw_event["eggs"], pogodata.get_mon)
        event.raids = __mon_list(raw_event["raids"], pogodata.get_mon)
        event.shinies = __mon_list(raw_event["shinies"], pogodata.get_mon)

        pogodata.events.append(event)
