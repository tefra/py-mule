from datetime import datetime
from enum import Enum, unique
from typing import List, Dict

from attr import attrib, attrs
from hashlib import md5
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


@attrs(frozen=True, auto_attribs=True)
class ResourceCabinClass(BaseModel):
    code: str
    name: str


@attrs(frozen=True, auto_attribs=True)
class ResourceCarrier(BaseModel):
    code: str
    logo: str
    name: str


@attrs(frozen=True, auto_attribs=True)
class ResourceEquipment(BaseModel):
    code: str
    name: str


@attrs(frozen=True, auto_attribs=True)
class ResourceLocation(BaseModel):
    code: str
    name: str
    country: str
    city: str


@attrs(frozen=True, auto_attribs=True)
class Resources(BaseModel):
    carriers: Dict[str, ResourceCarrier]
    cabinClasses: Dict[str, ResourceCabinClass]
    locations: Dict[str, ResourceLocation]
    equipments: Dict[str, ResourceEquipment]


@attrs(frozen=True, auto_attribs=True)
class Price(BaseModel):
    currency: str
    faceValue: float
    tax: float
    total: float


@attrs(frozen=True, auto_attribs=True)
class Passenger(BaseModel):
    count: int
    price: Price

    def get_total(self) -> float:
        return self.price.total * self.count;


@attrs(frozen=True, auto_attribs=True)
class Service(BaseModel):
    cabinClass: str
    bookingClass: str
    baggageAllowance: int


@attrs(frozen=True, auto_attribs=True)
class Point(BaseModel):
    location: str
    datetime: str


@attrs(frozen=True, auto_attribs=True)
class TechnicalStop(BaseModel):
    duration: int
    arrival: Point
    departure: Point


@attrs(frozen=True, auto_attribs=True)
class Route(BaseModel):
    departure: Point
    arrival: Point
    technicalStop: List[TechnicalStop]


@attrs(frozen=True, auto_attribs=True)
class LegService(BaseModel):
    numberOfSeats: int


@attrs(frozen=True, auto_attribs=True)
class Carrier(BaseModel):
    marketing: str
    operating: str


@attrs(frozen=True, auto_attribs=True)
class Transport(BaseModel):
    type: str
    number: str
    equipment: str
    carriers: Carrier


@attrs(frozen=True, auto_attribs=True)
class Segment(BaseModel):
    transport: Transport
    route: Route
    services: Service
    duration: int

    def generate_id(self) -> str:
        return ''.join([
            self.transport.number,
            self.transport.carriers.marketing,
            self.route.departure.datetime,
            self.route.arrival.datetime,
            self.route.departure.location,
            self.route.arrival.location,
            self.services.cabinClass
        ])


@attrs(frozen=True, auto_attribs=True)
class Leg(BaseModel):
    duration: int
    services: LegService
    segments: List[Segment]


@attrs(frozen=True, auto_attribs=True)
class Provider(BaseModel):
    name: str
    presentationName: str
    uri: str


@attrs(frozen=True, auto_attribs=True)
class SearchResponseData(BaseModel):
    id: str
    groupId: str
    provider: Provider
    resources: Resources
    legs: List[Leg]
    passengers: Dict[PassengerType, Passenger]

    def get_total(self) -> float:
        return sum([p.get_total() for p in self.passengers.values()])

    def generate_id(self) -> str:
        parts = [s.generate_id() for l in self.legs for s in l.segments]
        md5(''.join(parts)).digest()


@attrs(frozen=True, auto_attribs=True)
class SearchResponse(BaseModel):
    data: List[SearchResponseData]


@attrs(frozen=True, auto_attribs=True)
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
