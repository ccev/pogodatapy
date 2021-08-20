from typing import Dict, Any, List, Union

from .misc import GameObject
from .type import BaseType
from .icon import Icon


class WeatherIcon(Icon):
    day: bool

    def __init__(self, data: Dict[str, Union[str, bool]]):
        super().__init__(data["name"], data["url"])
        self.day = data["day"]


class BaseWeather(GameObject):
    endpoint = "weather"

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.tmpl = data["tmpl"]


class Weather(BaseWeather):
    name: str
    assets: List[WeatherIcon]
    boosts: List[BaseType]

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        self.name = data["name"]
        self.assets = [WeatherIcon(d) for d in data["assets"]]
        self.boosts = [BaseType(d) for d in data["boosts"]]

    def full(self):
        return self
