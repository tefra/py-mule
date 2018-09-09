from unittest import TestCase
from unittest.mock import Mock, patch

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

from search.mappers import SearchResponseMapper, SeeyaSearchRequestMapper
from search.models import SearchRequest
from search.services import SearchService
from seeya.models import SeeyaSearchRequest
from seeya.services import SeeyaClient

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
scheduler = TestScheduler()


class SearchServiceTestCase(TestCase):
    def test_providers(self):
        expected = ["petas", "figame", "kiwi", "travel2be", "travelgenio"]
        self.assertEqual(expected, SearchService().providers)

    @patch("search.services.scheduler", scheduler)
    @patch.object(SeeyaSearchRequestMapper, "map", return_value="foo")
    @patch.object(SearchService, "prepare")
    def test_perform(self, prepare, map):
        delays = {
            "petas": 40,
            "figame": 30,
            "kiwi": 10,
            "travel2be": 20,
            "travelgenio": 15,
        }

        def prep(p, *args):
            return Observable.return_value(p).delay(delays.get(p))

        prepare.side_effect = prep
        request = Mock(SearchRequest)

        service = SearchService()
        actual = [x for x in service.perform(request)]

        self.assertNotEqual(service.providers, actual)
        self.assertEqual(sorted(service.providers), sorted(actual))

    @patch("uuid.uuid4", Mock(return_value="12-34-56"))
    @patch("search.services.scheduler", scheduler)
    @patch.object(SearchService, "send", return_value="response")
    def test_prepare(self, send):
        request = SeeyaSearchRequest()
        res = scheduler.start(lambda: SearchService().prepare("out", request))
        expected = [on_next(200, "response"), on_completed(200)]
        self.assertEqual(expected, res.messages)

        request.transactionId = "12-34-56"
        request.provider = "out"
        send.assert_called_once_with(request)

    @patch("search.services.resources.enrich")
    @patch.object(SearchResponseMapper, "map", return_value="mapped_data")
    @patch.object(SeeyaClient, "send", return_value="communication")
    def test_send(self, client_send, mapper, enrich):
        request = Mock(SeeyaSearchRequest)
        enrich.side_effect = lambda x: x

        self.assertEqual(mapper.return_value, SearchService.send(request))
        mapper.assert_called_once_with(client_send.return_value)
