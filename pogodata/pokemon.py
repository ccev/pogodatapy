from __future__ import annotations
from typing import Dict, List, Union, Any, Optional, Type, TypeVar
from enum import Enum

from .enums import CustomEnum, EnumMatcher
from .icon import Icon
from .type import BaseType
from .misc import BaseApiObject


class Shiny(Enum):
    UNAVAILABLE = 0


class PokemonType(EnumMatcher):
    UNSET = 0
    BASE = 1
    FORM = 2
    TEMP_EVOLUTION = 3
    COSTUME = 4


class PokemonIcon(Icon):
    shiny: bool
    female: bool

    def __init__(self, data: Dict[str, Union[str, bool]]):
        super().__init__(data["name"], data["url"])
        self.shiny = data["shiny"]
        self.female = data["female"]


class BaseStats:
    attack: int
    defense: int
    stamina: int

    def __init__(self, data: List[int]):
        if len(data) != 3:
            self.data = (0, 0, 0)
        self.attack, self.defense, self.stamina = data

    def __repr__(self):
        return f"<BaseStats {self.__str__()}>"

    def __str__(self):
        return f"{self.attack}/{self.defense}/{self.stamina}"

    @property
    def atk(self) -> int:
        return self.attack

    @property
    def def_(self) -> int:
        return self.defense

    @property
    def sta(self) -> int:
        return self.stamina


class Encounter:
    base_capture_rate: float
    flee_rate: float
    attack_duration: float
    attack_probability: float
    dodge_duration: float
    dodge_probability: float
    dodge_distance: float

    def __init__(self, data: Dict[str, Union[float, Dict[str, float]]]):
        self.base_capture_rate = data["base_capture_rate"]
        self.flee_rate = data["flee_rate"]

        attack = data["attack"]
        self.attack_duration = attack["duration"]
        self.attack_probability = attack["probability"]

        dodge = data["dodge"]
        self.dodge_duration = dodge["duration"]
        self.dodge_probability = dodge["probability"]
        self.dodge_distance = dodge["distance"]

    @property
    def bcr(self) -> float:
        return self.base_capture_rate

    def __repr__(self):
        return f"<Encounter bcr={self.base_capture_rate} flee_rate={self.flee_rate}>"


class BasePokemon(BaseApiObject):
    endpoint = "pokemon"

    shiny: Shiny
    pokemon_type: PokemonType
    generation: CustomEnum
    pokemon: CustomEnum
    form: CustomEnum
    costume: CustomEnum
    temp_evolution: CustomEnum

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.shiny = data["shiny"]
        self.pokemon_type = PokemonType.match(data["pokemon_type"])
        self.generation = CustomEnum(data["generation"])
        self.pokemon = CustomEnum(data["pokemon"])
        self.form = CustomEnum(data["form"])
        self.costume = CustomEnum(data["costume"])
        self.temp_evolution = CustomEnum(data["temp_evolution"])

    def __repr__(self):
        return f"<Pokemon {self.id}>"

    def __str__(self):
        return self.form.tmpl

    def cp(self, level: int) -> int:
        pass  # TODO


class _BaseEvolution(BasePokemon):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data["into"])


class Evolution(_BaseEvolution):
    candy: Optional[int]
    quest: Optional[str]

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.candy = data["candy"]
        self.quest = data["quest"]


class TempEvolution(_BaseEvolution):
    energy_initial: int
    energy_subsequent: int

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.energy_initial = data["energy_initial"]
        self.energy_subsequent = data["energy_subsequent"]


class BaseMove:
    def __init__(self, d):
        pass


class Pokemon(BasePokemon):
    name: str
    form_name: str
    moves: List[BaseMove]
    elite_moves: List[BaseMove]
    types: List[BaseType]
    evolutions: List[Evolution]
    temp_evolutions: List[TempEvolution]
    base_stats: BaseStats
    assets: List[PokemonIcon]

    rarity: CustomEnum
    bonus_stardust: int
    bonus_candy: int
    bonus_xl: int
    deployable: bool
    tradable: bool
    transferable: bool
    buddy_distance: float
    height: float
    weight: float
    male_ratio: int
    female_ratio: int
    genderless_ratio: int
    third_move_candy: int
    third_move_stardust: int
    encounter: Encounter

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.name = data["name"]
        self.form_name = data["form_name"]
        self.moves = [BaseMove(d) for d in data["moves"]]
        self.elite_moves = [BaseMove(d) for d in data["elite_moves"]]
        self.types = [BaseType(d) for d in data["types"]]
        self.evolutions = [Evolution(d) for d in data["evolutions"]]
        self.temp_evolutions = [TempEvolution(d) for d in data["temp_evolutions"]]
        self.base_stats = BaseStats(data["base_stats"])
        self.assets = [PokemonIcon(d) for d in data["assets"]]

        info: Dict[str, Any] = data["info"]
        self.rarity = CustomEnum(info["rarity"])
        self.bonus_stardust = info["bonus_stardust"]
        self.bonus_candy = info["bonus_candy"]
        self.bonus_xl = info["bonus_xl"]
        self.deployable = info["deployable"]
        self.tradable = info["tradable"]
        self.transferable = info["transferable"]
        self.buddy_distance = info["buddy_distance"]
        self.height = info["height"]
        self.weight = info["weight"]

        gender_ratio: dict = info["gender_ratio"]
        self.male_ratio = gender_ratio["male"]
        self.female_ratio = gender_ratio["female"]
        self.genderless_ratio = gender_ratio["genderless"]

        third_move: dict = info["third_move"]
        self.third_move_candy = third_move["candy"]
        self.third_move_stardust = third_move["stardust"]

        self.encounter = Encounter(info["encounter"])

    def full(self):
        return self
