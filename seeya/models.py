from abc import ABCMeta
from enum import unique, Enum
from typing import List, Dict, Optional

from attr import attrib, attrs

from mule.converters import xstr
from mule.models import Serializable, CustomSerialization


@attrs(auto_attribs=True)
class SeeyaExcludedCarriers(Serializable):
    marketing: List[str] = attrib(factory=list)
    operating: List[str] = attrib(factory=list)
    validating: List[str] = attrib(factory=list)


@attrs(auto_attribs=True)
class SeeyaLeg(Serializable):
    dep: str
    arr: str
    date: str
    excludedCarriers: SeeyaExcludedCarriers
    depRadius: dict = attrib(factory=dict)
    arrRadius: dict = attrib(factory=dict)
    forceIncludedCarriers: list = attrib(factory=list)


@attrs(auto_attribs=True)
class SeeyaPassenger(Serializable):
    count: int
    type: str


@attrs(auto_attribs=True)
class SeeyaSearchQuery(Serializable):
    direct: bool
    preferredCarrier: str
    currency: str
    recommendedCabinClass: str
    legs: List[SeeyaLeg]
    passengers: List[SeeyaPassenger]
    pccs: list = attrib(factory=list)
    maxRecommendations: int = attrib(default=200)


@attrs(auto_attribs=True)
class SeeyaMetadata(Serializable):
    market: str
    locale: str


@attrs(auto_attribs=True)
class SeeyaRequest(Serializable, metaclass=ABCMeta):
    metadata: SeeyaMetadata = attrib(default=None)
    transactionId: str = attrib(default=None, converter=xstr)
    pcc: str = attrib(default=None)
    method: str = attrib(default=None)

    @property
    def provider(self):
        return None if self.method is None else self.method.split(".")[1]

    @provider.setter
    def provider(self, provider: str):
        self.method = ".".join([self.MODAL, provider, self.ACTION])


@attrs(auto_attribs=True)
class SeeyaSearchRequest(SeeyaRequest):
    MODAL = "flights"
    ACTION = "search"
    searchQuery: SeeyaSearchQuery = attrib(default=None)


@attrs(auto_attribs=True)
class SeeyaTechnicalStop(Serializable):
    destination: str
    duration: int
    depDatetime: str
    arrDatetime: str


@attrs(auto_attribs=True)
class SeeyaSegmentPoint(Serializable):
    airport: str
    datetime: str


@attrs(auto_attribs=True)
class SeeyaSegment(Serializable):
    dep: SeeyaSegmentPoint
    arr: SeeyaSegmentPoint
    marketingCarrier: str
    flightEquipment: str
    elapsedFlyingTime: int
    operatingCarrier: str
    flightNumber: str
    technicalStop: List[SeeyaTechnicalStop]


@attrs(auto_attribs=True)
class SeeyaPrice(Serializable):
    currency: str
    amount: float


@attrs(auto_attribs=True)
class SeeyaFareData(Serializable):
    proposedValidatingCarriers: List[str]
    totalPrice: SeeyaPrice
    taxes: SeeyaPrice
    baseFare: SeeyaPrice
    obFees: Dict[str, float]


@attrs(auto_attribs=True)
class SeeyaPaxFareData(Serializable):
    lastTicketingDatetime: Optional[str]
    fareBasis: str
    bookingClass: str
    refundable: bool
    numberOfSeats: int
    cabin: str


@attrs(auto_attribs=True)
class SeeyaPricePerPaxType(Serializable):
    totalPrice: SeeyaPrice
    baseFare: SeeyaPrice
    taxes: SeeyaPrice
    fareData: Dict[str, SeeyaPaxFareData]


@unique
class SeeyaPassengerType(Enum):
    adults = "ADT"
    children = "CHD"
    infants = "INF"


@attrs(auto_attribs=True)
class SeeyaSegmentReferences(CustomSerialization):
    data: List[List[str]]

    def __iter__(self):
        for elem in self.data:
            yield elem

    @classmethod
    def deserialize(cls, data):
        return cls(data=list(map(lambda d: [ref for ref, _ in d], data)))


@attrs(auto_attribs=True)
class SeeyaRecommendation(Serializable):
    pricePerPaxType: Dict[SeeyaPassengerType, SeeyaPricePerPaxType]
    segRefs: SeeyaSegmentReferences
    gds: str
    fareData: SeeyaFareData
    deepLink: str


@attrs(auto_attribs=True)
class SeeyaSearchResult(Serializable):
    transactionId: str
    groupOfSegments: Dict[str, SeeyaSegment]
    recommendations: List[SeeyaRecommendation]


@attrs(auto_attribs=True, slots=True)
class SeeyaSearchResponse(Serializable):
    transactionId: str
    result: Optional[SeeyaSearchResult]
    error: Optional[str]
