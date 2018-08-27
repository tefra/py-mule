from mule.testcases import TestCase
from seeya.models import SeeyaSearchReponse


class SeeyaSearchReponseTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_deserialization(self):
        original = self.resource(__name__, 'fixtures/search.json')
        deserialized = self.resource(__name__, 'fixtures/search_ds.json')
        response = SeeyaSearchReponse.from_json(original)
        self.assertJSONEqual(deserialized, response.to_json())
