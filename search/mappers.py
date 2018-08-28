from functools import singledispatch
from typing import Dict, Any

from mule.models import BaseMapper
from search.models import (
    SearchRequest, PassengerRequest, RouteRequest, SearchResponse, Segment,
    Route, TechnicalStop, Point, Transport, Carrier, SearchResponseData,
    Passenger, Price, Services, Leg, Provider
)
from seeya.models import (
    SeeyaSearchRequest, SeeyaLeg, SeeyaPassenger, SeeyaSearchQuery,
    SeeyaMetadata, SeeyaExcludedCarriers, SeeyaSearchResponse, SeeyaSegment,
    SeeyaTechnicalStop, SeeyaSegmentPoint, SeeyaRecommendation,
    SeeyaPricePerPaxType, SeeyaPassengerType, SeeyaSegmentReferences,
    SeeyaPaxFareData
)


@singledispatch
def to_seeya(value):
    return value


class SeeyaSearchRequestMapper(BaseMapper):
    func = to_seeya


@singledispatch
def from_seeya(value):
    return value


class SearchResponseMapper(BaseMapper):
    func = from_seeya


@to_seeya.register(list)
def _(value: list) -> list:
    return list(map(to_seeya, value))


@to_seeya.register(SearchRequest)
def _(value: SearchRequest) -> SeeyaSearchRequest:
    return SeeyaSearchRequest(
        searchQuery=SeeyaSearchQuery(
            direct=value.directRoutes,
            preferredCarrier=value.carrier,
            currency=value.currency,
            recommendedCabinClass=value.cabinClass,
            legs=to_seeya(value.routes),
            passengers=to_seeya(value.passengers)
        ),
        metadata=SeeyaMetadata(market=value.market, locale=value.locale)
    )


@to_seeya.register(RouteRequest)
def _(value: RouteRequest) -> SeeyaLeg:
    return SeeyaLeg(
        dep=value.departure,
        arr=value.arrival,
        date=value.datetime.replace('T', ' '),
        excludedCarriers=SeeyaExcludedCarriers()
    )


@to_seeya.register(PassengerRequest)
def _(value: PassengerRequest) -> SeeyaPassenger:
    return SeeyaPassenger(
        count=value.count,
        type=value.type.name
    )


@from_seeya.register(list)
def _(value: list, *args, **kwargs) -> list:
    return list(map(lambda x: from_seeya(x, *args, **kwargs), value))


@from_seeya.register(dict)
def _(value: dict) -> dict:
    return {from_seeya(k): from_seeya(v) for k, v in value.items()}


@from_seeya.register(SeeyaSearchResponse)
def _(value: SeeyaSearchResponse) -> SearchResponse:
    data = []
    error = value.error
    if error is None:
        segments = from_seeya(value.result.groupOfSegments)
        data = from_seeya(value.result.recommendations, segments=segments)

    return SearchResponse(data=data, error=error)


@from_seeya.register(SeeyaRecommendation)
def _(value: SeeyaRecommendation,
      segments: Dict[str, Segment]) -> SearchResponseData:
    faredata = value.pricePerPaxType.get(SeeyaPassengerType.adults).fareData
    return SearchResponseData(
        id=None,
        provider=Provider(name=value.gds, uri=value.deepLink),
        legs=from_seeya(value.segRefs, segments=segments, faredata=faredata),
        passengers=from_seeya(value.pricePerPaxType)
    )


@from_seeya.register(SeeyaSegmentReferences)
def _(value: SeeyaSegmentReferences, segments: Dict[str, Segment],
      faredata: SeeyaPaxFareData) -> str:
    def get_segment(ref):
        return segments.get(ref).copy(services=Services(
            cabinClass=faredata.get(ref).cabin,
            bookingClass=faredata.get(ref).bookingClass
        ))

    def create_leg(refs):
        segments = [get_segment(ref) for ref in refs]
        return Leg(segments=segments)

    return list(map(create_leg, value))


@from_seeya.register(SeeyaPassengerType)
def _(value: SeeyaPassengerType) -> str:
    return value.name


@from_seeya.register(SeeyaPricePerPaxType)
def _(value: SeeyaPricePerPaxType) -> Passenger:
    return Passenger(count=0, price=Price(
        total=value.totalPrice.amount,
        currency=value.totalPrice.currency,
        tax=value.taxes.amount,
        faceValue=value.baseFare.amount
    ))


@from_seeya.register(SeeyaSegment)
def _(value: SeeyaSegment) -> Segment:
    transport = Transport(
        type='flights',
        number=value.flightNumber,
        equipment=value.flightEquipment,
        carriers=Carrier(
            marketing=value.marketingCarrier,
            operating=value.operatingCarrier
        )
    )

    route = Route(
        departure=from_seeya(value.dep),
        arrival=from_seeya(value.arr),
        technicalStop=from_seeya(value.technicalStop)
    )

    return Segment(
        transport=transport,
        route=route,
        duration=value.elapsedFlyingTime
    )


@from_seeya.register(SeeyaSegmentPoint)
def _(value: SeeyaSegmentPoint):
    return Point(location=value.airport, datetime=value.datetime)


@from_seeya.register(SeeyaTechnicalStop)
def _(value: SeeyaTechnicalStop) -> TechnicalStop:
    return TechnicalStop(
        arrival=Point(location=value.destination, datetime=value.arrDatetime),
        departure=Point(location=value.destination, datetime=value.depDatetime),
        duration=value.duration
    )
