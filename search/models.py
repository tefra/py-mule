import hashlib
from enum import Enum, unique
from typing import List, Dict, Optional

from attr import attrib, attrs

from mule.models import Serializable
from search.validators import Regex, Datetime


@attrs(auto_attribs=True)
class RouteRequest(Serializable):
    departure: str = attrib(validator=Regex("[A-Z]{3}"))
    arrival: str = attrib(validator=Regex("[A-Z]{3}"))
    datetime: str = attrib(validator=Datetime("%Y-%m-%dT%H:%M:%S"))


@unique
class PassengerType(Enum):
    ADT = "adults"
    CHD = "children"
    INF = "infants"


@unique
class CabinClassType(Enum):
    ECONOMY = "Y"
    STANDARD_ECONOMY = "M"
    PREMIUM_ECONOMY = "W"
    BUSINESS = "C"
    FIRST = "F"


@attrs(auto_attribs=True)
class PassengerRequest(Serializable):
    count: int
    type: PassengerType


@attrs(auto_attribs=True)
class SearchRequest(Serializable):
    routes: List[RouteRequest]
    passengers: List[PassengerRequest] = attrib()
    cabinClass: CabinClassType = attrib()
    carrier: str = attrib(validator=Regex("([A-Z0-9]{2})?"))
    flexibleDates: bool
    locale: str
    currency: str
    market: str
    directRoutes: bool = attrib(default=False)

    def get_passengers_by_type(self, type: PassengerType):
        for pax in self.passengers:
            if pax.type == type:
                return pax

    # @passengers.validator
    # def validate_passengers(self, attr, value):
    #     adt = self.get_passengers_by_type(PassengerType.ADT).count
    #     chd = self.get_passengers_by_type(PassengerType.CHD).count
    #     inf = self.get_passengers_by_type(PassengerType.INF).count
    #
    #     evaluate(adt > 0 and adt > inf, name=attr.name, value=value)
    #     evaluate((adt + chd) < 9, name=attr.name, value=value)


@attrs(auto_attribs=True)
class ResourceCabinClass(Serializable):
    code: str
    name: str


@attrs(auto_attribs=True)
class ResourceCarrier(Serializable):
    code: str
    logo: Optional[str]
    name: str


@attrs(auto_attribs=True)
class ResourceEquipment(Serializable):
    code: str
    name: str


@attrs(auto_attribs=True)
class ResourceLocation(Serializable):
    code: str
    name: str
    country: str
    city: str


@attrs(auto_attribs=True)
class Resources(Serializable):
    carriers: Dict[str, ResourceCarrier]
    cabinClasses: Dict[str, ResourceCabinClass]
    locations: Dict[str, ResourceLocation]
    equipments: Dict[str, ResourceEquipment]

    def all(self):
        return (
            (ResourceCarrier, self.carriers),
            (ResourceCabinClass, self.cabinClasses),
            (ResourceLocation, self.locations),
            (ResourceEquipment, self.equipments),
        )


@attrs(auto_attribs=True)
class Price(Serializable):
    currency: str
    faceValue: float
    tax: float
    total: float


@attrs(auto_attribs=True)
class Passenger(Serializable):
    count: int
    price: Price

    def get_total(self) -> float:
        return self.price.total * self.count


@attrs(auto_attribs=True)
class Services(Serializable):
    cabinClass: str
    bookingClass: str


@attrs(auto_attribs=True)
class Point(Serializable):
    location: str
    datetime: str


@attrs(auto_attribs=True)
class TechnicalStop(Serializable):
    duration: int
    arrival: Point
    departure: Point


@attrs(auto_attribs=True)
class Route(Serializable):
    departure: Point
    arrival: Point
    technicalStop: List[TechnicalStop]


@attrs(auto_attribs=True)
class Carrier(Serializable):
    marketing: str
    operating: str


@attrs(auto_attribs=True)
class Transport(Serializable):
    type: str
    number: str
    equipment: str
    carriers: Carrier


@attrs(auto_attribs=True)
class Segment(Serializable):
    transport: Transport
    route: Route
    duration: int
    services: Services = attrib(default=None)

    def generate_id(self) -> str:
        return "".join(
            [
                self.transport.number,
                self.transport.carriers.marketing,
                self.route.departure.datetime,
                self.route.arrival.datetime,
                self.route.departure.location,
                self.route.arrival.location,
                self.services.cabinClass,
            ]
        )


@attrs(auto_attribs=True)
class Leg(Serializable):
    segments: List[Segment]
    duration: int = attrib(init=False, default=None)


@attrs(auto_attribs=True)
class Provider(Serializable):
    name: str
    uri: str
    presentationName: str = attrib(init=False)

    def __attrs_post_init__(self):
        self.presentationName = self.name


@attrs(auto_attribs=True)
class SearchResponseData(Serializable):
    id: str
    groupId: str = attrib(init=False)
    provider: Provider
    resources: Resources = attrib(init=False)
    legs: List[Leg]
    passengers: Dict[PassengerType, Passenger]

    def __attrs_post_init__(self):
        self.groupId = self.generate_group_id()
        self.resources = self.generate_resources()

    def get_total(self) -> float:
        return sum([p.get_total() for p in self.passengers.values()])

    def generate_group_id(self) -> str:
        parts = [s.generate_id() for l in self.legs for s in l.segments]
        return hashlib.md5("".join(parts).encode(encoding="utf-8")).hexdigest()

    def generate_resources(self) -> Resources:
        carriers = dict()
        classes = dict()
        locations = dict()
        equipments = dict()

        for leg in self.legs:
            for segment in leg.segments:
                carriers.setdefault(segment.transport.carriers.marketing, None)
                carriers.setdefault(segment.transport.carriers.operating, None)
                equipments.setdefault(segment.transport.equipment, None)
                classes.setdefault(segment.services.cabinClass, None)

                locations.setdefault(segment.route.departure.location, None)
                locations.setdefault(segment.route.arrival.location, None)
                for stop in segment.route.technicalStop:
                    locations.setdefault(stop.arrival.location, None)
                    locations.setdefault(stop.departure.location, None)

        return Resources(
            carriers=carriers,
            cabinClasses=classes,
            locations=locations,
            equipments=equipments,
        )


@attrs(auto_attribs=True)
class SearchResponse(Serializable):
    data: List[SearchResponseData]
    locale: str
    error: Optional[str]
