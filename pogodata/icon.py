from typing import Dict, Type, TypeVar, Union

from .enums import EnumMatcher


I_ = TypeVar("I_", bound="Icon")


class Icon:
    name: str
    url: str

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    @classmethod
    def from_data(cls: Type[I_], data: Dict[str, Union[str, bool]]) -> I_:
        return cls(data["name"], data["url"])

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self):
        return self.url

    def read(self):
        pass  # TODO

    def save(self):
        pass  # TODO


class IconSet(EnumMatcher):
    POGO = 0
    POGO_OPTIMIZED = 1
    POGO_OUTLINE = 2
    # COPYRIGHTSAFE = 10
    # THEARTIFICIAL = 11
    HOME = 20
    HOME_OUTLINE = 21
    SHUFFLE = 30
    SUGIMORI_OPTIMIZED = 40
    DERP_AFD = 50
    DERP_FLORK = 51
    # PIXEL_GEN3 = 60