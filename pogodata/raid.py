from .misc import httpget, INFO_URL

class RaidIterator:
    def __init__(self, raids):
        self.mons = []
        for level, mon in raids.items():
            self.mons += [m for m in mon]
        self._index = 0

    def __next__(self):
        if self._index < len(self.mons):
            result = self.mons[self._index]
            self._index += 1
            return result
        raise StopIteration

class Raids:
    def __init__(self):
        self.raids = {}

    def add_mon(self, level, mon):
        level = int(level)
        if level not in self.raids:
            self.raids[level] = []
        
        mon = mon.copy()
        mon.level = level
        self.raids[level].append(mon)

    def __iter__(self):
        return RaidIterator(self.raids)

    def __getitem__(self, key):
        return self.raids.get(key, [])

def _make_raid_list(pogodata):
    pogodata.raids = Raids()
    raw_raids = httpget(INFO_URL + "active/raids.json").json()
    for level, mons in raw_raids.items():
        for raw_mon in mons:
            if not raw_mon:
                continue
            mon = pogodata.get_mon(**raw_mon)

            if mon:
                pogodata.raids.add_mon(level, mon)