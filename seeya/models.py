from abc import ABCMeta, abstractmethod
from typing import List, Dict, Any, Optional

from attr import attrib, attrs

from mule.converters import xstr
from mule.models import BaseModel


@attrs(frozen=True, auto_attribs=True)
class SearchQueryExcludedCarriers(BaseModel):
    marketing: List[str] = attrib(factory=list)
    operating: List[str] = attrib(factory=list)
    validating: List[str] = attrib(factory=list)


@attrs(frozen=True, auto_attribs=True)
class SearchQueryLeg(BaseModel):
    dep: str
    arr: str
    date: str
    excludedCarriers: SearchQueryExcludedCarriers
    depRadius: dict = attrib(factory=dict)
    arrRadius: dict = attrib(factory=dict)
    forceIncludedCarriers: list = attrib(factory=list)


@attrs(frozen=True, auto_attribs=True)
class SearchQueryPassenger(BaseModel):
    count: int
    type: str


@attrs(frozen=True, auto_attribs=True)
class SearchQuery(BaseModel):
    direct: bool
    preferredCarrier: str
    currency: str
    recommendedCabinClass: str
    legs: List[SearchQueryLeg]
    passengers: List[SearchQueryPassenger]
    pccs: list = attrib(factory=list)
    maxRecommendations: int = attrib(default=200)


@attrs(frozen=True, auto_attribs=True)
class Metadata(BaseModel):
    market: str
    locale: str


@attrs(frozen=True)
class SeeyaRequest(BaseModel, metaclass=ABCMeta):
    metadata: Metadata = attrib()
    transactionId: str = attrib(default=None, converter=xstr)
    pcc: str = attrib(default=None)
    method: str = attrib(
        default=None,
        converter=lambda x: 'flights.{}.search'.format(x)
    )

    @property
    def provider(self):
        return self.method.split('.')[1]

    @property
    @abstractmethod
    def type(self):
        pass


@attrs(frozen=True, auto_attribs=True)
class SeeyaSearchRequest(SeeyaRequest):
    searchQuery: SearchQuery = attrib(default=None)  # kw_only coming soon

    @property
    def type(self):
        return 'search'


@attrs(frozen=True, auto_attribs=True)
class SegmentTechnicalStop(BaseModel):
    destination: str
    duration: int
    depDatetime: str
    arrDatetime: str


@attrs(frozen=True, auto_attribs=True)
class SegmentPoint(BaseModel):
    terminal: Optional[str]
    airport: str
    gmtOffset: Optional[str]
    datetime: str


@attrs(frozen=True, auto_attribs=True)
class Segment(BaseModel):
    dep: SegmentPoint
    arr: SegmentPoint
    marketingCarrier: str
    flightEquipment: str
    elapsedFlyingTime: int
    operatingCarrier: str
    flightNumber: str
    technicalStop: List[SegmentTechnicalStop]
    metadata: Any


@attrs(frozen=True, auto_attribs=True)
class Price(BaseModel):
    currency: str
    amount: float


@attrs(frozen=True, auto_attribs=True)
class FareData(BaseModel):
    proposedValidatingCarriers: List[str]
    totalPrice: Price
    taxes: Price
    baseFare: Price
    obFees: Dict[str, float]
    ancillaryServices: Any


@attrs(frozen=True, auto_attribs=True)
class PaxFareData(BaseModel):
    lastTicketingDatetime: Optional[str]
    fareBasis: str
    bookingClass: str
    refundable: bool
    numberOfSeats: int
    cabin: str
    baggage: Any
    fareRefKey: Any = attrib(default=None)
    fareRuleKey: Any = attrib(default=None)
    providerCode: Any = attrib(default=None)


@attrs(frozen=True, auto_attribs=True)
class PricePerPaxType(BaseModel):
    totalPrice: Price
    fareData: Dict[str, PaxFareData]
    baseFare: Price
    taxes: Price


@attrs(frozen=True, auto_attribs=True)
class ConnectionData(BaseModel):
    lapsedFlyingTimes: List[int]
    connectionIDs: List[str]


@attrs(frozen=True, auto_attribs=True)
class SegmentReference(BaseModel):
    uniqueId: str
    connectionIndicator: bool


def map_seg_refs(data):
    return list(map(lambda d: [SegmentReference(x, y) for x, y in d], data))


@attrs(frozen=True, auto_attribs=True)
class Recommendation(BaseModel):
    pricePerPaxType: Dict[str, PricePerPaxType]
    segRefs: List[List[Any]] = attrib(converter=map_seg_refs)
    gds: str
    fareData: FareData
    deepLink: str
    connectionData: ConnectionData = attrib(default=None)


@attrs(frozen=True, auto_attribs=True)
class SearchResult(BaseModel):
    transactionId: str
    method: str
    groupOfSegments: Dict[str, Segment]
    recommendations: List[Recommendation]


@attrs(frozen=True, auto_attribs=True, slots=True)
class SeeyaSearchReponse(BaseModel):
    transactionId: str
    result: Optional[SearchResult]
    error: Optional[str]
