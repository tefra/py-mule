from typing import Dict, TypeVar

from attr import evolve
from cattr import unstructure, structure
from json import loads, dumps

T = TypeVar('T', bound='BaseModel')


class BaseModel:

    def to_dict(self: T) -> Dict:
        return unstructure(self)

    def to_json(self: T, indent=4, **kwargs) -> str:
        return dumps(unstructure(self), indent=indent, **kwargs)

    def copy(self: T, **kwargs) -> T:
        return evolve(self, **kwargs)

    @classmethod
    def from_json(cls: T, stream) -> T:
        stream = stream.read() if hasattr(stream, 'read') else stream
        data = loads(stream)

        if isinstance(data, list) and len(data) == 1:
            data = data[0]

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls: T, data: dict) -> T:
        return structure(data, cls)
