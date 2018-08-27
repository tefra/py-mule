from django import test

import pkg_resources


class TestCase(test.TestCase):
    @staticmethod
    def resource(package, resource):
        return pkg_resources.resource_string(package, resource)
