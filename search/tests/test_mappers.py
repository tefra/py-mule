from unittest.mock import patch, call

from attr import attrs, attrib

from mule.models import Serializable
from mule.testcases import TestCase
from search.mappers import SeeyaSearchRequestMapper, SearchResponseMapper
from search.models import (
    SearchRequest, RouteRequest, PassengerRequest, PassengerType, Leg,
    SearchResponseData)
from seeya.models import (
    SeeyaSearchResponse, SeeyaSearchResult, SeeyaSegment,
    SeeyaSegmentPoint, SeeyaTechnicalStop, SeeyaPricePerPaxType, SeeyaPrice,
    SeeyaPassengerType, SeeyaSegmentReferences,
    SeeyaRecommendation)


@attrs(auto_attribs=True)
class FooFareData(Serializable):
    cabin: str
    bookingClass: str


@attrs(auto_attribs=True)
class FooSegment(Serializable):
    cabinClass: str = attrib(default=None)
    bookingClass: str = attrib(default=None)

    @classmethod
    def copy(cls, **kwargs):
        return cls(kwargs)


class SeeyaSearchRequestMapperTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.mapper = SeeyaSearchRequestMapper()

    @patch.object(SeeyaSearchRequestMapper, 'map_routes')
    @patch.object(SeeyaSearchRequestMapper, 'map_passengers')
    def test_map(self, map_passengers, map_routes):
        map_routes.return_value = 'bar'
        map_passengers.return_value = 'foo'

        actual = self.mapper.map(SearchRequest(
            routes='bar',
            passengers='foo',
            cabinClass='A',
            carrier='AB',
            flexibleDates=True,
            locale='en_US',
            currency='USD',
            market='US',
            directRoutes=False
        ))

        expected = {
            'metadata': {'locale': 'en_US', 'market': 'US'},
            'method': 'flights.None.search',
            'pcc': None,
            'searchQuery': {
                'currency': 'USD',
                'direct': False,
                'legs': 'bar',
                'maxRecommendations': 200,
                'passengers': 'foo',
                'pccs': [],
                'preferredCarrier': 'AB',
                'recommendedCabinClass': 'A'
            },
            'transactionId': ''
        }
        self.assertEqual(expected, actual.to_dict())

        actual.provider = 'foobar'
        self.assertEqual('flights.foobar.search', actual.method)

    @patch.object(SeeyaSearchRequestMapper, 'map_route')
    def test_map_routes(self, map_route):
        map_route.side_effect = ['a', 'b', 'c']
        self.assertEqual(['a', 'b', 'c'], self.mapper.map_routes([1, 2, 3]))

    def test_map_route(self):
        actual = self.mapper.map_route(RouteRequest(
            departure='ATH',
            arrival='SKG',
            datetime='2018-12-31T12:12:06'
        ))

        expected = {
            'arr': 'SKG',
            'arrRadius': {},
            'date': '2018-12-31 12:12:06',
            'dep': 'ATH',
            'depRadius': {},
            'excludedCarriers': {
                'marketing': [], 'operating': [], 'validating': []
            },
            'forceIncludedCarriers': []
        }
        self.assertEqual(expected, actual.to_dict())

    @patch.object(SeeyaSearchRequestMapper, 'map_passenger')
    def test_map_passengers(self, map_passenger):
        map_passenger.side_effect = ['a', 'b', 'c']
        self.assertEqual(['a', 'b', 'c'], self.mapper.map_passengers([1, 2, 3]))

    def test_map_passenger(self):
        actual = self.mapper.map_passenger(PassengerRequest(
            count=2, type=PassengerType.CHD
        ))

        expected = {'count': 2, 'type': 'CHD'}
        self.assertEqual(expected, actual.to_dict())


class SearchResponseMapperTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.mapper = SearchResponseMapper()

    @patch.object(SearchResponseMapper, 'map_recommendations')
    @patch.object(SearchResponseMapper, 'map_segments')
    def test_map(self, map_segments, map_recommendations):
        map_segments.return_value = 'bar'
        map_recommendations.return_value = 'foo'

        actual = self.mapper.map(SeeyaSearchResponse(
            transactionId='foo',
            error=None,
            result=SeeyaSearchResult(
                transactionId='bar',
                groupOfSegments='foo',
                recommendations='bar',
            )
        ))

        expected = {'data': 'foo', 'error': None}
        self.assertEqual(expected, actual.to_dict())

        map_segments.assert_called_once_with('foo')
        map_recommendations.assert_called_once_with('bar')

    def test_map_with_error(self):
        actual = self.mapper.map(SeeyaSearchResponse(
            transactionId='foo',
            result=['resultA', 'resultB'],
            error='damn'
        ))

        expected = {'data': [], 'error': 'damn'}
        self.assertEqual(expected, actual.to_dict())

    @patch.object(SearchResponseData, 'generate_resources')
    @patch.object(SearchResponseData, 'generate_group_id')
    @patch.object(SearchResponseMapper, 'map_passengers')
    @patch.object(SearchResponseMapper, 'map_legs')
    def test_map_recommendation(self, map_legs, map_passengers, id, resources):
        id.return_value = '$id'
        resources.return_value = '$resources'

        map_legs.return_value = ['legs']
        map_passengers.return_value = ['paxes']

        @attrs(auto_attribs=True)
        class FooPrice:
            fareData: int

        prices = {
            SeeyaPassengerType.adults: FooPrice(2)
        }

        actual = self.mapper.map_recommendation(SeeyaRecommendation(
            gds='kiwi',
            deepLink='google.com',
            segRefs=['a', 'b'],
            pricePerPaxType=prices,
            fareData=None
        ))

        expected = {
            'groupId': '$id',
            'id': None,
            'legs': ['legs'],
            'passengers': ['paxes'],
            'provider': {
                'name': 'kiwi', 'presentationName': 'kiwi', 'uri': 'google.com'
            },
            'resources': '$resources'
        }
        self.assertEqual(expected, actual.to_dict())

    @patch.object(SearchResponseMapper, 'map_segment')
    def test_map_routes(self, map_segment):
        map_segment.side_effect = ['a', 'b', 'c']
        self.assertEqual(['a', 'b', 'c'], self.mapper.map_segments([1, 2, 3]))

    @patch.object(SearchResponseMapper, 'map_technical_stops')
    @patch.object(SearchResponseMapper, 'map_point')
    def test_map_segment(self, map_point, map_stops):
        map_point.side_effect = ['a', 'b']
        map_stops.return_value = ['c']

        actual = self.mapper.map_segment(SeeyaSegment(
            dep='fooDep',
            arr='fooArr',
            marketingCarrier='AB',
            operatingCarrier='BA',
            elapsedFlyingTime=60,
            flightEquipment='747',
            flightNumber='1003',
            technicalStop=[]
        ))

        expected = {
            'duration': 60,
            'route': {'arrival': 'b', 'departure': 'a', 'technicalStop': ['c']},
            'services': None,
            'transport': {
                'carriers': {'marketing': 'AB', 'operating': 'BA'},
                'equipment': '747',
                'number': '1003',
                'type': 'flights'
            }
        }
        self.assertEqual(expected, actual.to_dict())

    def test_map_point(self):
        actual = self.mapper.map_point(SeeyaSegmentPoint(
            airport='ATH',
            datetime='2018-12-12 15:30:00'
        ))

        expected = {'datetime': '2018-12-12 15:30:00', 'location': 'ATH'}
        self.assertEqual(expected, actual.to_dict())

    @patch.object(SearchResponseMapper, 'map_technical_stop')
    def test_map_routes(self, map_technical_stop):
        map_technical_stop.side_effect = ['a', 'c']
        self.assertEqual(['a', 'c'], self.mapper.map_technical_stops([1, 3]))

    def test_map_technical_stop(self):
        actual = self.mapper.map_technical_stop(SeeyaTechnicalStop(
            destination='ATH',
            duration=15,
            arrDatetime='2018-12-12 13:30:00',
            depDatetime='2018-12-12 15:30:00'
        ))

        expected = {
            'arrival': {'datetime': '2018-12-12 13:30:00', 'location': 'ATH'},
            'departure': {'datetime': '2018-12-12 15:30:00', 'location': 'ATH'},
            'duration': 15
        }

        self.assertEqual(expected, actual.to_dict())

    @patch.object(SearchResponseMapper, 'map_passenger')
    def test_map_passengers(self, map_passenger):
        map_passenger.side_effect = ['d', 'e', 'f']

        segments = {
            SeeyaPassengerType.adults: 'a',
            SeeyaPassengerType.children: 'b',
            SeeyaPassengerType.infants: 'c'
        }
        self.mapper.map_passengers(segments)

        map_passenger.assert_has_calls([call('a'), call('b'), call('c')])

    def test_map_passenger(self):
        actual = self.mapper.map_passenger(SeeyaPricePerPaxType(
            totalPrice=SeeyaPrice(amount=100, currency='USD'),
            taxes=SeeyaPrice(amount=10, currency=''),
            baseFare=SeeyaPrice(amount=90, currency=''),
            fareData={'a': 1, 'b': 2}
        ))

        expected = {
            'count': 0,
            'price': {
                'currency': 'USD',
                'faceValue': 90,
                'tax': 10,
                'total': 100
            }
        }
        self.assertEqual(expected, actual.to_dict())

    def test_map_legs(self):
        refs = SeeyaSegmentReferences.deserialize(
            [[('aaa', True)], [('bbb', False), ('ccc', True)]]
        )

        faredata = dict(
            aaa=FooFareData('A', 'A!'),
            bbb=FooFareData('B', 'B!'),
            ccc=FooFareData('C', 'C!')
        )

        self.mapper.segments = dict(
            aaa=FooSegment(),
            bbb=FooSegment(),
            ccc=FooSegment(),
        )

        actual = self.mapper.map_legs(refs, data=faredata)
        self.assertEqual(2, len(actual))

        first = {
            'duration': None,
            'segments': [{
                'bookingClass': None,
                'cabinClass': {
                    'services': {
                        'bookingClass': 'A!',
                        'cabinClass': 'A'
                    }
                }
            }],
        }
        second = {
            'duration': None,
            'segments': [{
                'bookingClass': None,
                'cabinClass': {
                    'services': {
                        'bookingClass': 'B!',
                        'cabinClass': 'B'
                    }
                }
            },
                {
                    'bookingClass': None,
                    'cabinClass': {
                        'services': {
                            'bookingClass': 'C!',
                            'cabinClass': 'C'
                        }
                    }
                }]
        }

        self.assertIsInstance(actual[0], Leg)
        self.assertIsInstance(actual[1], Leg)

        self.assertEqual(first, actual[0].to_dict())
        self.assertEqual(second, actual[1].to_dict())
