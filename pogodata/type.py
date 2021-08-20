from typing import List, Dict, Any

from .misc import GameObject


class BaseType(GameObject):
    endpoint = "types"

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.tmpl = data["tmpl"]


class Type(BaseType):
    name: str
    effective_against: List[BaseType]
    weak_against: List[BaseType]
    resists: List[BaseType]
    resisted_by: List[BaseType]

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        self.effective_against = [BaseType(d) for d in data["effective_against"]]
        self.weak_against = [BaseType(d) for d in data["weak_against"]]
        self.resists = [BaseType(d) for d in data["resists"]]
        self.resisted_by = [BaseType(d) for d in data["resisted_by"]]

    def full(self):
        return self
