import re
from abc import ABCMeta
from datetime import datetime

from attr import attrs, attrib


class Validate(metaclass=ABCMeta):
    message = "'{name}' recieved an invalid value `{value!s}`"

    @classmethod
    def evaluate(cls, result, **kwargs):
        if not result:
            message = (
                kwargs.pop("message") if kwargs.get("message") else cls.message
            )
            raise ValueError(message.format(**kwargs))


evaluate = Validate.evaluate


@attrs(slots=True, hash=True)
class Regex(Validate):
    regex: str = attrib(converter=lambda x: "^{}$".format(x))

    def __call__(self, inst, attr, value):
        result = re.compile(self.regex).match(value)
        return self.evaluate(result, name=attr.name, value=value)


@attrs(slots=True, hash=True, auto_attribs=True)
class Datetime(Validate):
    format: str

    def __call__(self, inst, attr, value):
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return self.evaluate(False, name=attr.name, value=value)
