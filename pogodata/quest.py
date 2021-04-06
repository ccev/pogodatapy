from enum import Enum

class QuestType(Enum):
    UNSET = 0
    BASE = 1
    EVENT = 2
    SPONSORED = 3
    AR = 4

class Quest:
    def __init__(self):
        pass