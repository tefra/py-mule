from django.test import TestCase
from rest_framework.mixins import ListModelMixin
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from resources.filters import MultiValueFilter
from resources.models import Airport, Airline
from resources.serializers import AirportSerializer, AirlineSerializer
from resources.views import AirportViewSet, AirlineViewSet

mixin_classes = (ListModelMixin, GenericViewSet)


class AirportViewSetTestCase(TestCase):
    def test_properties(self):
        self.assertTrue(issubclass(AirportViewSet, mixin_classes))
        self.assertEqual(Airport.objects, AirportViewSet.queryset)
        self.assertEqual(AirportSerializer, AirportViewSet.serializer_class)
        self.assertEqual("[A-Za-z]{3}", AirportViewSet.lookup_value_regex)
        self.assertEqual("code", AirportViewSet.lookup_field)
        self.assertEqual((MultiValueFilter,), CountryViewSet.filter_backends)
        self.assertEqual("/resources/airports/", reverse("airport-list"))


class AirlineViewSetTestCase(TestCase):
    def test_properties(self):
        self.assertTrue(issubclass(AirlineViewSet, mixin_classes))
        self.assertEqual(Airline.objects, AirlineViewSet.queryset)
        self.assertEqual(AirlineSerializer, AirlineViewSet.serializer_class)
        self.assertEqual("[A-Za-z0-9]{2}", AirlineViewSet.lookup_value_regex)
        self.assertEqual("code", AirlineViewSet.lookup_field)
        self.assertEqual((MultiValueFilter,), CountryViewSet.filter_backends)
        self.assertEqual("/resources/airlines/", reverse("airline-list"))
