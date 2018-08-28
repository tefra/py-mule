from mule.testcases import TestCase
from search.mappers import SearchResponseMapper

from seeya.models import SeeyaSearchResponse


class SearchReponseTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_deserialization(self):
        original = self.resource('mule', 'fixtures/seeya_rs.json')
        expected = self.resource('mule', 'fixtures/api_rs.json')
        response = SeeyaSearchResponse.from_json(original)
        actual = SearchResponseMapper.map(response)
        self.assertJSONEqual(expected, actual.to_json())
