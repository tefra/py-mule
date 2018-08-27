from mule.testcases import TestCase
from search.models import RouteRequest

import attr


class RouteRequestTest(TestCase):

    def test_validations(self):
        with self.assertRaisesRegex(ValueError, 'is not a valid 3letter code'):
            RouteRequest(departure=None, arrival='SKG', datetime=None)

        with self.assertRaisesRegex(ValueError, 'is not a valid 3letter code'):
            RouteRequest(departure='ATH', arrival='', datetime=None)

        with self.assertRaisesRegex(ValueError, 'must be str, not None'):
            RouteRequest(departure='ATH', arrival='SKG', datetime=None)

        with self.assertRaisesRegex(ValueError, 'does not match format'):
            RouteRequest(
                departure='ATH',
                arrival='SKG',
                datetime='2018-12-32T00:05:06'
            )

        foo = RouteRequest.from_json('{"departure":"ATH", "arrival": "SKG", "datetime": "2018-12-30T00:05:06"}')
        RouteRequest.datetime

        attr.validate(RouteRequest(
            departure='ATH',
            arrival='SKG',
            datetime='2018-12-03T00:05:06'
        ))
