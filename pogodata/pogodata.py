from __future__ import annotations
from typing import Optional, Union, Dict, Any, List, Type

from .http import SyncHttp, AsyncHttp
from .enums import Language
from .icon import IconSet
from .pokemon import Pokemon
from .move import Move
from .type import Type
from .weather import Weather
from .misc import BaseApiObject
from .raids import Raids


class _PogoData:
    _language: Language
    _iconset: IconSet
    _http: Union[SyncHttp, AsyncHttp]

    def __init__(self,
                 host: str = "localhost:4442",
                 language: Union[Language, str] = Language.ENGLISH,
                 iconset: Union[IconSet, str] = IconSet.POGO):
        if isinstance(language, str):
            self._language = Language.match(language)
        else:
            self._language = language

        if isinstance(iconset, str):
            self._iconset = IconSet.match(iconset)
        else:
            self._iconset = iconset

    @staticmethod
    def __parse_language_or_iconset(value: Any,
                                    enum: Union[Type[IconSet], Type[Language]],
                                    default: Union[IconSet, Language]) -> str:
        if not value:
            return default.value
        elif isinstance(value, enum):
            return value.value
        else:
            return enum.match(value).value

    def _parse_language_iconset(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        kwargs["iconset"] = self.__parse_language_or_iconset(
            kwargs.get("iconset"), IconSet, self._iconset)

        kwargs["language"] = self.__parse_language_or_iconset(
            kwargs.get("language"), Language, self._language)

        return kwargs


class PogoData(_PogoData):
    def __init__(self,
                 host: str = "localhost:4442",
                 language: Union[Language, str] = Language.ENGLISH,
                 iconset: Union[IconSet, str] = IconSet.POGO):
        super().__init__(host, language, iconset)
        self._http = SyncHttp(host)

    def __get_base(self, kwargs: dict, obj: BaseApiObject) -> List[BaseApiObject]:
        kwargs = self._parse_language_iconset(kwargs)
        raw_mons = self._http.get(obj.endpoint, body=kwargs)
        return [obj(d) for d in raw_mons]

    def get_pokemon(self, **kwargs) -> List[Pokemon]:
        return self.__get_base(kwargs, Pokemon)

    def get_mons(self, **kwargs) -> List[Pokemon]:
        """
        Alias for PogoData.get_pokemon
        """
        return self.get_pokemon(**kwargs)

    def get_moves(self, **kwargs) -> List[Move]:
        return self.__get_base(kwargs, Move)

    def get_raids(self) -> Raids:
        raids = Raids()
        raw_raids = self._http.get_info(Raids.endpoint)
        for level, mons in raw_raids.items():
            for raw_mon in mons:
                if not raw_mon:
                    continue
                if "id" in raw_mon:
                    raw_mon["pokemon"] = raw_mon.pop("id")
                if "template" in raw_mon:
                    raw_mon["form"] = raw_mon.pop("template")
                if "temp_evolution_id" in raw_mon:
                    raw_mon["temp_evolution"] = raw_mon.pop("temp_evolution_id")
                mons = self.get_mons(**raw_mon)

                if len(mons) == 0:
                    continue
                mon = mons[0]
                if mon:
                    raids.add_mon(level, mon)
        return raids


class AioPogoData(_PogoData):
    def __init__(self,
                 host: str = "localhost:4442",
                 language: Union[Language, str] = Language.ENGLISH,
                 iconset: Union[IconSet, str] = IconSet.POGO):
        super().__init__(host, language, iconset)
        self._http = AsyncHttp(host)

    async def get_pokemon(self, **kwargs) -> List[Pokemon]:
        raw_mons = await self._http.get(Pokemon.endpoint, body=kwargs)
        return [Pokemon(d) for d in raw_mons]

    async def get_mons(self, **kwargs) -> List[Pokemon]:
        """
        Alias for AioPogoData.get_pokemon
        """
        return await self.get_pokemon(**kwargs)
