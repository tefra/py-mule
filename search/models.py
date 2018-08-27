from datetime import datetime
from enum import Enum, unique
from typing import List

from attr import attrib, attrs

from mule.converters import upper
from mule.models import BaseModel


def validate_iso_date(_, attr, value):
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        TypeError
        raise ValueError(str(e))


@attrs(frozen=True, auto_attribs=True)
class RouteRequest(BaseModel):
    departure: str = attrib(converter=upper)
    arrival: str = attrib(converter=upper)
    datetime: str = attrib(validator=validate_iso_date)


@unique
class PassengerType(Enum):
    ADT = 'adults'
    CHD = 'children'
    INF = 'infants'


@attrs(frozen=True, auto_attribs=True)
class PassengerRequest(BaseModel):
    count: int
    type: PassengerType


@attrs(frozen=True, auto_attribs=True)
class SearchRequest(BaseModel):
    routes: List[RouteRequest]
    passengers: List[PassengerRequest]
    cabinClass: str
    carrier: str
    flexibleDates: bool
    locale: str
    currency: str
    market: str
    directRoutes: bool = attrib(default=False)
