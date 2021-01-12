class RaidIterator:
    def __init__(self, raids):
        self.mons = []
        for mon in raids.values():
            self.mons += mon
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
        
        self.raids[level].append(mon)

    def __iter__(self):
        return RaidIterator(self.raids)

    def __getitem__(self, key):
        return self.raids.get(key, [])
