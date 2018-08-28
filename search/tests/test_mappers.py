from attr import attrs, attrib

from mule.models import Serializable
from mule.testcases import TestCase
from search.mappers import SeeyaSearchRequestMapper, to_seeya, from_seeya, \
    SearchResponseMapper
from search.models import SearchRequest, RouteRequest, PassengerRequest, \
    PassengerType, Leg
from seeya.models import SeeyaSearchResponse, SeeyaSearchResult, SeeyaSegment, \
    SeeyaSegmentPoint, SeeyaTechnicalStop, SeeyaPricePerPaxType, SeeyaPrice, \
    SeeyaPassengerType, SeeyaSegmentReferences, SeeyaRecommendation


@from_seeya.register(str)
@to_seeya.register(str)
def _(value: str, **kwargs) -> str:
    return ''.join(kwargs.keys()) + '@' + value


@from_seeya.register(int)
@to_seeya.register(int)
def _(value: int, **kwargs) -> int:
    return str(value)


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
    mapper = SeeyaSearchRequestMapper

    def test_map_list(self):
        actual = self.mapper.map([1, 2, 3])
        self.assertEqual(['1', '2', '3'], actual)

    def test_map_str(self):
        self.assertEqual('@foo', self.mapper.map('foo'))

    def test_map_search_request(self):
        actual = self.mapper.map(SearchRequest(
            routes=['route1', 'route2'],
            passengers=['paxA', 'paxB'],
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
                'legs': ['@route1', '@route2'],
                'maxRecommendations': 200,
                'passengers': ['@paxA', '@paxB'],
                'pccs': [],
                'preferredCarrier': 'AB',
                'recommendedCabinClass': 'A'
            },
            'transactionId': ''
        }
        self.assertEqual(expected, actual.to_dict())

        actual.provider = 'foobar'
        self.assertEqual('flights.foobar.search', actual.method)

    def test_map_route_request(self):
        actual = self.mapper.map(RouteRequest(
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

    def test_map_passenger_request(self):
        actual = self.mapper.map(PassengerRequest(
            count=2, type=PassengerType.CHD
        ))

        expected = {'count': 2, 'type': 'CHD'}
        self.assertEqual(expected, actual.to_dict())


class SearchResponseMapperTestCase(TestCase):
    mapper = SearchResponseMapper

    def test_map_list(self):
        actual = self.mapper.map([1, 2, 3])
        self.assertEqual(['1', '2', '3'], actual)

    def test_map_str(self):
        self.assertEqual('@foo', self.mapper.map('foo'))

    def test_map_dict(self):
        actual = self.mapper.map({'a': '1', 'b': '2'})
        self.assertEqual({'@a': '@1', '@b': '@2'}, actual)

    def test_map_str(self):
        self.assertEqual('@foo', self.mapper.map('foo'))

    def test_map_seeya_search_response(self):
        actual = self.mapper.map(SeeyaSearchResponse(
            transactionId='foo',
            result=SeeyaSearchResult(
                transactionId='bar',
                groupOfSegments={'a': '1', 'b': '2'},
                recommendations=['fareA', 'fareB']),
            error=None
        ))

        expected = {'data': ['segments@fareA', 'segments@fareB'], 'error': None}
        self.assertEqual(expected, actual.to_dict())

    def test_map_seeya_search_response_with_error(self):
        actual = self.mapper.map(SeeyaSearchResponse(
            transactionId='foo',
            result=['resultA', 'resultB'],
            error='damn'
        ))

        expected = {'data': [], 'error': 'damn'}
        self.assertEqual(expected, actual.to_dict())

    def test_map_seeya_segment(self):
        actual = self.mapper.map(SeeyaSegment(
            dep='fooDep',
            arr='fooArr',
            marketingCarrier='AB',
            operatingCarrier='BA',
            elapsedFlyingTime=60,
            flightEquipment='747',
            flightNumber='1003',
            technicalStop=[1, 2]
        ))

        expected = {
            'duration': 60,
            'route': {
                'arrival': '@fooArr', 'departure': '@fooDep',
                'technicalStop': ['1', '2']
            },
            'services': None,
            'transport': {
                'carriers': {'marketing': 'AB', 'operating': 'BA'},
                'equipment': '747',
                'number': '1003',
                'type': 'flights'
            }
        }
        self.assertEqual(expected, actual.to_dict())

    def test_map_seeya_segment_point(self):
        actual = self.mapper.map(SeeyaSegmentPoint(
            airport='ATH',
            datetime='2018-12-12 15:30:00'
        ))

        expected = {'datetime': '2018-12-12 15:30:00', 'location': 'ATH'}
        self.assertEqual(expected, actual.to_dict())

    def test_map_seeya_technical_stop(self):
        actual = self.mapper.map(SeeyaTechnicalStop(
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

    def test_map_seeya_price_per_pax_type(self):
        actual = self.mapper.map(SeeyaPricePerPaxType(
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

    def test_map_seeya_passenger_type(self):
        types = SeeyaPassengerType
        self.assertEqual('adults', self.mapper.map(types.adults))
        self.assertEqual('children', self.mapper.map(types.children))
        self.assertEqual('infants', self.mapper.map(types.infants))

    def test_map_seeya_segment_references(self):
        refs = SeeyaSegmentReferences.deserialize(
            [[('aaa', True)], [('bbb', False), ('ccc', True)]]
        )

        faredata = dict(
            aaa=FooFareData('A', 'A!'),
            bbb=FooFareData('B', 'B!'),
            ccc=FooFareData('C', 'C!')
        )

        segments = dict(
            aaa=FooSegment(),
            bbb=FooSegment(),
            ccc=FooSegment(),
        )

        actual = self.mapper.map(refs, segments=segments, faredata=faredata)
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
