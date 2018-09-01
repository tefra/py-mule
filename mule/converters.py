import json
from collections import namedtuple
from typing import Optional, Any, Dict


def upper(value: Optional[str]):
    return "" if value is None else value.upper()


def xstr(value: Any):
    return "" if value is None else str(value)


def obj(value: Dict):
    def hook(d):
        return namedtuple("X", d.keys())(*d.values())

    return json.loads(json.dumps(value), object_hook=hook)
