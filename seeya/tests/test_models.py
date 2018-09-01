from mule.testcases import TestCase
from seeya.models import SeeyaSearchResponse


class SeeyaSearchReponseTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_deserialization(self):
        original = self.resource(__name__, "fixtures/seeya_rs.json")
        deserialized = self.resource(__name__, "fixtures/seeya_ds.json")
        response = SeeyaSearchResponse.from_json(original)
        self.assertJSONEqual(deserialized, response.to_json())
