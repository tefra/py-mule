from datetime import datetime
from enum import Enum, unique
from typing import List

from attr import attrib, attrs

from mule.converters import upper
from mule.models import BaseModel
from seeya.models import SearchQueryLeg, SearchQueryExcludedCarriers, \
    SearchQueryPassenger, Metadata, SearchQuery, SeeyaSearchRequest


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


class SearchRequestMapper:
    Passengers = List[PassengerRequest]
    SeeyaPassengers = List[SearchQueryPassenger]
    Routes = List[RouteRequest]
    SeeyaLegs = List[SearchQueryLeg]

    @classmethod
    def to_seeya(cls, request: SearchRequest) -> SeeyaSearchRequest:
        return SeeyaSearchRequest(
            searchQuery=SearchQuery(
                direct=request.directRoutes,
                preferredCarrier=request.carrier,
                currency=request.currency,
                recommendedCabinClass=request.cabinClass,
                legs=cls.convert_routes(request.routes),
                passengers=cls.convert_passengers(request.passengers)
            ),
            metadata=Metadata(market=request.market, locale=request.locale)
        )

    @classmethod
    def convert_passengers(cls, passengers: Passengers) -> SeeyaPassengers:
        def create_passenger(x: PassengerRequest) -> SearchQueryPassenger:
            return SearchQueryPassenger(
                count=x.count,
                type=x.type.name
            )

        return [create_passenger(passenger) for passenger in passengers]

    @classmethod
    def convert_routes(cls, routes: Routes) -> SeeyaLegs:
        def create_leg(x: RouteRequest) -> SearchQueryLeg:
            return SearchQueryLeg(
                dep=x.departure,
                arr=x.arrival,
                date=x.datetime.replace('T', ' '),
                excludedCarriers=SearchQueryExcludedCarriers()
            )

        return [create_leg(route) for route in routes]
