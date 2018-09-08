from mule.testcases import TestCase
from seeya.models import SeeyaSearchResponse, SeeyaSearchRequest, SeeyaRequest


class SeeyaSearchReponseTest(TestCase):
    def test_deserialization(self):
        original = self.resource(__name__, "fixtures/seeya_rs.json")
        deserialized = self.resource(__name__, "fixtures/seeya_ds.json")
        response = SeeyaSearchResponse.from_json(original)
        self.assertJSONEqual(deserialized, response.to_json())


class SeeyaSearchRequestTest(TestCase):
    def test_constants(self):
        self.assertTrue(issubclass(SeeyaSearchRequest, SeeyaRequest))
        self.assertEqual("flights", SeeyaSearchRequest.MODAL)
        self.assertEqual("search", SeeyaSearchRequest.ACTION)


class SeeyaRequestTestCase(TestCase):
    def test_provider_property(self):
        request = SeeyaRequest()

        self.assertFalse(hasattr(request, "MODAL"))
        self.assertFalse(hasattr(request, "ACTION"))
        self.assertIsNone(request.provider)
        self.assertIsNone(request.method)

        with self.assertRaises(AttributeError):
            request.provider = "me"
        request.MODAL = "bus"

        with self.assertRaises(AttributeError):
            request.provider = "me"

        request.ACTION = "wait"
        request.provider = "me"
        self.assertEqual("bus.me.wait", request.method)
        self.assertEqual("me", request.provider)
