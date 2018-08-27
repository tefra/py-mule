from typing import Optional, Any


def upper(value: Optional[str]):
    return '' if value is None else value.upper()


def xstr(value: Any):
    return '' if value is None else str(value)
