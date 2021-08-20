from typing import Dict, Union
from enum import Enum


class CustomEnum:
    id: int
    tmpl: str

    def __init__(self, data: Dict[str, Union[int, str]]):
        self.id = data["id"]
        self.tmpl = data["tmpl"]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.tmpl}:{self.id}>"


class EnumMatcher(Enum):
    @classmethod
    def match(cls, value: Union[str, int]):
        enum_list = list(cls)
        if value.upper() in [e.name for e in enum_list]:
            return cls[value.upper()]
        elif value in [e.value for e in enum_list]:
            return cls(value)
        else:
            return enum_list[0]


class Language(EnumMatcher):
    ENGLISH = "English"
    BRAZILIANPORTUGUESE = "BrazilianPortuguese"
    CHINESETRADITIONAL = "ChineseTraditional"
    FRENCH = "French"
    GERMAN = "German"
    ITALIAN = "Italian"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    THAI = "Thai"

    # Aliases
    BRAZILIAN = "BrazilianPortuguese"
    PORTUGUESE = "BrazilianPortuguese"
    PTBR = "BrazilianPortuguese"
    CHINESE = "ChineseTraditional"
    ZH = "ChineseTraditional"
    CH = "ChineseTraditional"
    EN = "English"
    DE = "German"
    IT = "Italian"
    JA = "Japanese"
    JP = "Japanese"
    KO = "Korean"
    ES = "Spanish"
    TH = "Thai"