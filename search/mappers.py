from typing import Dict, List

from attr import attrs, attrib

from search.models import (
    PassengerRequest,
    RouteRequest,
    SearchResponse,
    Segment,
    Route,
    TechnicalStop,
    Point,
    Transport,
    Carrier,
    SearchResponseData,
    Passenger,
    Price,
    Services,
    Leg,
    Provider,
    PassengerType,
)
from seeya.models import (
    SeeyaSearchRequest,
    SeeyaLeg,
    SeeyaPassenger,
    SeeyaSearchQuery,
    SeeyaMetadata,
    SeeyaExcludedCarriers,
    SeeyaSearchResponse,
    SeeyaSegment,
    SeeyaTechnicalStop,
    SeeyaSegmentPoint,
    SeeyaRecommendation,
    SeeyaPricePerPaxType,
    SeeyaPassengerType,
    SeeyaSegmentReferences,
    SeeyaPaxFareData,
)


class SeeyaSearchRequestMapper:
    Passengers = List[PassengerRequest]
    SeeyaPassengers = List[SeeyaPassenger]

    def map(self, value: SearchResponse) -> SeeyaSearchResponse:
        legs = self.map_routes(value.routes)
        passengers = self.map_passengers(value.passengers)

        return SeeyaSearchRequest(
            searchQuery=SeeyaSearchQuery(
                direct=value.directRoutes,
                preferredCarrier=value.carrier,
                currency=value.currency,
                recommendedCabinClass=value.cabinClass,
                legs=legs,
                passengers=passengers,
            ),
            metadata=SeeyaMetadata(market=value.market, locale=value.locale),
        )

    def map_routes(self, value: List[RouteRequest]) -> List[SeeyaLeg]:
        return list(map(lambda x: self.map_route(x), value))

    @staticmethod
    def map_route(value: RouteRequest) -> SeeyaLeg:
        return SeeyaLeg(
            dep=value.departure,
            arr=value.arrival,
            date=value.datetime.replace("T", " "),
            excludedCarriers=SeeyaExcludedCarriers(),
        )

    def map_passengers(self, value: Passengers) -> SeeyaPassengers:
        return list(map(lambda x: self.map_passenger(x), value))

    @staticmethod
    def map_passenger(value: PassengerRequest) -> SeeyaPassenger:
        return SeeyaPassenger(count=value.count, type=value.type.name)


@attrs
class SearchResponseMapper:
    request: SeeyaSearchRequest = attrib()
    segments: Dict[str, Segment] = attrib(default=dict())

    Passengers = Dict[PassengerType, Passenger]
    SeeyaPassengers = Dict[SeeyaPassengerType, SeeyaPricePerPaxType]
    Segments = Dict[str, Segment]
    SeeyaSegments = Dict[str, SeeyaSegment]
    Recommendation = SeeyaRecommendation
    Recommendations = List[Recommendation]
    ResponseData = List[SearchResponseData]
    SeeyaTechnicalStops = List[SeeyaTechnicalStop]
    TechnicalStops = List[TechnicalStop]
    SegRefs = SeeyaSegmentReferences

    def map(self, value: SeeyaSearchResponse) -> SearchResponse:
        data = []
        error = value.error
        locale = self.request.metadata.locale
        if error is None:
            self.segments = self.map_segments(value.result.groupOfSegments)
            data = self.map_recommendations(value.result.recommendations)

        return SearchResponse(data=data, error=error, locale=locale)

    def map_recommendations(self, value: Recommendations) -> ResponseData:
        return list(map(lambda x: self.map_recommendation(x), value))

    def map_segments(self, value: SeeyaSegments) -> Segments:
        return {k: self.map_segment(v) for k, v in value.items()}

    def map_segment(self, value: SeeyaSegment) -> Segment:
        transport = Transport(
            type="flights",
            number=value.flightNumber,
            equipment=value.flightEquipment,
            carriers=Carrier(
                marketing=value.marketingCarrier,
                operating=value.operatingCarrier,
            ),
        )

        route = Route(
            departure=self.map_point(value.dep),
            arrival=self.map_point(value.arr),
            technicalStop=self.map_technical_stops(value.technicalStop),
        )

        return Segment(
            transport=transport, route=route, duration=value.elapsedFlyingTime
        )

    def map_point(self, value: SeeyaSegmentPoint) -> Point:
        return Point(location=value.airport, datetime=value.datetime)

    def map_technical_stops(self, val: SeeyaTechnicalStops) -> TechnicalStops:
        return list(map(lambda x: self.map_technical_stop(x), val))

    @staticmethod
    def map_technical_stop(value: SeeyaTechnicalStop) -> TechnicalStop:
        return TechnicalStop(
            arrival=Point(
                location=value.destination, datetime=value.arrDatetime
            ),
            departure=Point(
                location=value.destination, datetime=value.depDatetime
            ),
            duration=value.duration,
        )

    def map_recommendation(self, value: Recommendation) -> SearchResponseData:
        adults = value.pricePerPaxType.get(SeeyaPassengerType.adults)

        return SearchResponseData(
            id=None,
            provider=Provider(name=value.gds, uri=value.deepLink),
            legs=self.map_legs(value.segRefs, data=adults.fareData),
            passengers=self.map_passengers(value.pricePerPaxType),
        )

    def map_legs(self, value: SegRefs, data: SeeyaPaxFareData) -> List[Leg]:
        def get_segment(ref):
            return self.segments.get(ref).copy(
                services=Services(
                    cabinClass=data.get(ref).cabin,
                    bookingClass=data.get(ref).bookingClass,
                )
            )

        def create_leg(refs):
            segments = [get_segment(ref) for ref in refs]
            return Leg(segments=segments)

        return list(map(create_leg, value))

    def map_passengers(self, value: SeeyaPassengers) -> Passengers:
        return {k.name: self.map_passenger(v) for k, v in value.items()}

    @staticmethod
    def map_passenger(value: SeeyaPricePerPaxType) -> Passenger:
        return Passenger(
            count=0,
            price=Price(
                total=value.totalPrice.amount,
                currency=value.totalPrice.currency,
                tax=value.taxes.amount,
                faceValue=value.baseFare.amount,
            ),
        )
