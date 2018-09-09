from typing import List
from unittest import TestCase
from unittest.mock import patch, call, Mock

from attr import attrs
from cachetools.keys import hashkey
from requests import Response

from search.managers import ResourceManager
from search.models import (
    Resources,
    ResourceCarrier,
    ResourceEquipment,
    ResourceLocation,
    ResourceCabinClass,
)


@attrs(auto_attribs=True)
class SearchResponseData:
    resources: Resources


@attrs(auto_attribs=True)
class SearchResponse:
    data: List[SearchResponseData]
    locale: str


locale = "en_US"


class ResourceManagerTestCase(TestCase):
    def setUp(self):
        self.manager = ResourceManager()

    @patch.object(ResourceManager, "filter_codes")
    @patch.object(ResourceManager, "get")
    @patch.object(ResourceManager, "fetch")
    def test_enrich(self, fetch, get, filter):
        filter.side_effect = lambda x: x

        data = dict(
            carriers=dict.fromkeys(["A3", "LH"]),
            cabinClasses=dict.fromkeys(["Y", "C"]),
            equipments=dict(),
            locations=dict.fromkeys(["ATH", "SKG"]),
        )
        resources = Resources(**data)
        response = SearchResponse([SearchResponseData(resources)], locale)

        self.manager.enrich(response)

        fetch.assert_has_calls(
            [
                call(ResourceCarrier, locale, data.get("carriers").keys()),
                call(
                    ResourceCabinClass, locale, data.get("cabinClasses").keys()
                ),
                call(ResourceLocation, locale, data.get("locations").keys()),
                call(ResourceEquipment, locale, data.get("equipments").keys()),
            ]
        )

        get.assert_has_calls(
            [
                call(ResourceCarrier, locale, "A3"),
                call(ResourceCarrier, locale, "LH"),
                call(ResourceCabinClass, locale, "Y"),
                call(ResourceCabinClass, locale, "C"),
                call(ResourceLocation, locale, "ATH"),
                call(ResourceLocation, locale, "SKG"),
            ]
        )

    def test_filter_codes(self):
        def run(codes):
            return self.manager.filter_codes(ResourceCarrier, locale, codes)

        self.assertEqual([], run(None))
        self.assertEqual([], run([]))
        self.assertEqual(["A3"], run("A3"))

        for x in ["A3", "LH"]:
            key = hashkey(self.manager, ResourceCarrier, locale, x)
            self.manager.cache[key] = x

        self.assertEqual(["CY", "FR"], run(["A3", "CY", "LH", "FR"]))

    @patch.object(ResourceManager, "fetch", return_value="bar")
    def test_get(self, *args):
        def run(code):
            return self.manager.get(ResourceCarrier, locale, code)

        key = hashkey(self.manager, ResourceCarrier, locale, "A3")
        self.manager.cache[key] = "foo"

        self.assertEqual("foo", run("A3"))
        self.assertEqual("bar", run("SKG"))

    def test_fetch_with_no_code(self):
        manager = ResourceManager()
        actual = manager.fetch(ResourceCarrier, locale, [])
        self.assertIsNone(actual)

    @patch("search.managers.logger.exception")
    @patch("requests.get", side_effect=TimeoutError("too slow"))
    def test_fetch_with_communication(self, get, logger):
        actual = self.manager.fetch(ResourceCarrier, locale, "A3")
        self.assertIsNone(actual)

        logger.assert_called_once_with("TimeoutError('too slow',)")

    @patch("search.managers.logger.exception")
    @patch("requests.get", return_value=Response())
    def test_fetch_with_not_found(self, get, logger):
        response = get.return_value
        response.status_code = 404
        actual = self.manager.fetch(ResourceCarrier, locale, "A3")
        self.assertIsNone(actual)

        message = "HTTPError('404 Client Error: None for url: None',)"
        logger.assert_called_once_with(message)

    @patch("requests.get", return_value=Response())
    def test_fetch_with_one_code(self, get):
        response = get.return_value
        response.status_code = 200
        response.json = Mock(
            return_value=[dict(code="A3", logo=None, name="Aegean", foo="bar")]
        )

        actual = self.manager.fetch(ResourceCarrier, locale, "A3")
        expected = ResourceCarrier(code="A3", logo=None, name="Aegean")
        self.assertEqual(expected, actual)
        self.assertEqual(1, self.manager.cache.currsize)
        key = hashkey(self.manager, ResourceCarrier, locale, "A3")
        self.assertTrue(key in self.manager.cache)

    @patch("requests.get", return_value=Response())
    def test_fetch_with_multiple_codes(self, get):
        response = get.return_value
        response.status_code = 200
        response.json = Mock(
            return_value=[
                dict(code="A3", logo=None, name="Aegean", foo="bar"),
                dict(code="LH", logo="lh.gif", name="Luff", bar="foo"),
            ]
        )

        actual = self.manager.fetch(ResourceCarrier, locale, "A3")
        self.assertIsNone(actual)
        self.assertEqual(2, self.manager.cache.currsize)

        for x in ["A3", "LH"]:
            key = hashkey(self.manager, ResourceCarrier, locale, x)
            self.assertTrue(key in self.manager.cache)
