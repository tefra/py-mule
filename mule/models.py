from typing import Dict, TypeVar

import cattr
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


def structure_attrs_fromdict(obj, cl):
    # type: (Mapping, Type) -> Any
    """Instantiate an attrs class from a mapping (dict) that ignores unknown
    fields `cattr issue <https://github.com/Tinche/cattrs/issues/35>`_"""
    # For public use.

    # conv_obj = obj.copy()  # Dict of converted parameters.
    conv_obj = dict()  # Start fresh

    # dispatch = self._structure_func.dispatch
    dispatch = cattr.global_converter._structure_func.dispatch  # Ugly I know
    for a in cl.__attrs_attrs__:
        # We detect the type by metadata.
        type_ = a.type
        if type_ is None:
            # No type.
            continue
        name = a.name
        try:
            val = obj[name]
        except KeyError:
            continue
        conv_obj[name] = dispatch(type_)(val, type_)

    return cl(**conv_obj)


cattr.register_structure_hook(BaseModel, structure_attrs_fromdict)
