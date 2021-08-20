from typing import Union

from .http import _Http


class BaseApiObject:
    id: Union[int, str]
    endpoint: str
    _http: _Http

    def __init__(self, http: _Http):
        self._http = http


class GameObject(BaseApiObject):
    tmpl: str

    def __repr__(self):
        return f"<{type(self).__name__} {self.tmpl}:{self.id}>"

    def __str__(self):
        return self.tmpl
