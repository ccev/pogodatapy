from typing import Dict, Any

from .misc import GameObject
from .type import BaseType


class Pvp:
    power: int
    energy_gain: int

    def __init__(self, data: Dict[str, Any]):
        self.power = data["power"]
        self.energy_gain = data["energy_gain"]

    def __repr__(self):
        return f"<{self.__class__.__name__} Stats power={self.power} energy_gain={self.energy_gain}>"


class Pve(Pvp):
    duration: int
    window_start: float
    window_end: float

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.duration = data["duration"]
        window = data["window"]
        self.window_start = window["start"]
        self.window_end = window["end"]


class BaseMove(GameObject):
    endpoint = "moves"
    type: BaseType

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.tmpl = data["tmpl"]
        self.type = BaseType(data["type"])


class Move(BaseMove):
    name: str
    pve: Pve
    pvp: Pvp

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        self.name = data["name"]
        self.pve = Pve(data["pve"])
        self.pvp = Pvp(data["pvp"])

    def full(self):
        return self
