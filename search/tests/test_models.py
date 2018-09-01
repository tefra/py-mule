import hashlib
from unittest import TestCase
from unittest.mock import patch

from attr import attrs

from mule.converters import obj
from mule.models import Serializable
from search.models import Segment, SearchResponseData, Leg, Price, Passenger


class SegmentTestCase(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(Segment, Serializable))

    def test_generate_id(self):
        segment = Segment.deserialize(
            {
                "transport": {
                    "type": "flights",
                    "number": "10",
                    "equipment": "1000",
                    "carriers": {"marketing": "QF", "operating": "AB"},
                },
                "route": {
                    "departure": {
                        "location": "LHR",
                        "datetime": "2018-09-08 13:15:00",
                    },
                    "arrival": {
                        "location": "MEL",
                        "datetime": "2018-09-09 20:00:00",
                    },
                    "technicalStop": [
                        {
                            "duration": 90,
                            "arrival": {
                                "location": "PER",
                                "datetime": "2018-09-09 13:00:00",
                            },
                            "departure": {
                                "location": "PER",
                                "datetime": "2018-09-09 14:30:00",
                            },
                        }
                    ],
                },
                "duration": 1305,
                "services": {"cabinClass": "Y", "bookingClass": "V"},
            }
        )

        expected = "10QF2018-09-08 13:15:002018-09-09 20:00:00LHRMELY"
        self.assertEqual(expected, segment.generate_id())


class SearchResponseDataTestCase(TestCase):
    @patch.object(SearchResponseData, "generate_resources")
    @patch.object(SearchResponseData, "generate_group_id")
    def test_point_init_calls(self, generate_group_id, generate_resources):
        SearchResponseData(id=None, provider=None, legs=None, passengers=None)
        generate_group_id.assert_called_once_with()
        generate_resources.assert_called_once_with()

    @patch.object(SearchResponseData, "generate_group_id")
    @patch.object(SearchResponseData, "generate_resources")
    def test_get_total(self, *args):
        @attrs(auto_attribs=True)
        class Pax:
            total: float

            def get_total(self):
                return self.total

        data = SearchResponseData(
            id=None,
            provider=None,
            legs=None,
            passengers={"foo": Pax(1.1), "bar": Pax(2.2), "foobar": Pax(3.3)},
        )
        self.assertEqual(6.6, data.get_total())

    @patch.object(SearchResponseData, "generate_resources")
    def test_generate_group_id(self, *args):
        @attrs(auto_attribs=True)
        class Seg:
            id: str

            def generate_id(self):
                return self.id

        data = SearchResponseData(
            id=None,
            provider=None,
            passengers=None,
            legs=[
                Leg(segments=[Seg("A"), Seg("B")]),
                Leg(segments=[Seg("B")]),
                Leg(segments=[Seg("C"), Seg("D")]),
            ],
        )

        expected = hashlib.md5("ABBCD".encode(encoding="utf-8")).hexdigest()
        actual = data.generate_group_id()
        self.assertEqual(expected, data.generate_group_id())
        self.assertRegex(actual, "^[a-fA-F\d]{32}$")

    @patch.object(SearchResponseData, "generate_group_id")
    def test_generate_resources(self, *args):
        segment = obj(
            dict(
                transport=dict(
                    carriers=dict(marketing="OA", operating="A3"),
                    equipment="747",
                ),
                services=dict(cabinClass="A"),
                route=dict(
                    departure=dict(location="ATH"),
                    arrival=dict(location="SKG"),
                    technicalStop=[
                        dict(
                            departure=dict(location="LHR"),
                            arrival=dict(location="MJT"),
                        )
                    ],
                ),
            )
        )

        legs = [Leg(segments=[segment])]
        data = SearchResponseData(
            id=None, provider=None, passengers=None, legs=legs
        )

        expected = {
            "cabinClasses": {"A": None},
            "carriers": {"A3": None, "OA": None},
            "equipments": {"747": None},
            "locations": {"ATH": None, "LHR": None, "MJT": None, "SKG": None},
        }
        self.assertDictEqual(expected, data.generate_resources().to_dict())


class PassengerTestCase(TestCase):
    def test_get_total(self):
        passenger = Passenger(
            2, Price(currency="USD", faceValue=1, tax=2, total=3)
        )

        self.assertEqual(6, passenger.get_total())
