from typing import Union


class BaseApiObject:
    id: Union[int, str]
    endpoint: str

    def full(self):
        pass  # TODO


class GameObject(BaseApiObject):
    tmpl: str

    def __repr__(self):
        return f"<{type(self).__name__} {self.tmpl}:{self.id}>"

    def __str__(self):
        return self.tmpl
