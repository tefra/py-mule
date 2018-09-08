from collections import OrderedDict

from django.test import TestCase
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from resources.models import Continent, Country, Airline, Airport
from resources.serializers import (
    CountrySerializer,
    AirlineSerializer,
    AirportSerializer,
)

mixin_classes = (ListModelMixin, GenericViewSet)


class ContinentTestCase(TestCase):
    def test_choices(self):
        result = list(Continent.choices())
        expected = [
            ("Africa", "AFRICA"),
            ("Asia", "ASIA"),
            ("Caribbean", "CARIBBEAN"),
            ("North America", "NORTH_AMERICA"),
            ("Central America", "CENTRAL_AMERICA"),
            ("South America", "SOUTH_AMERICA"),
            ("Oceania", "OCEANIA"),
            ("Europe", "EUROPE"),
        ]
        self.assertEqual(expected, result)

    def test_str_return_value(self):
        self.assertEqual(Continent.AFRICA.value, str(Continent.AFRICA))


class CountryTestCase(TestCase):
    def test_save_convert_codes_to_uppercase(self):
        Country(
            code="gr",
            iso_code="gre",
            name="Greece",
            continent=Continent.EUROPE,
            dialingCode="+030",
        ).save()

        serializer = CountrySerializer(Country.objects.all(), many=True)
        expected = [
            OrderedDict(
                [
                    ("code", "GR"),
                    ("iso_code", "GRE"),
                    ("name", "Greece"),
                    ("continent", "Europe"),
                    ("dialingCode", "+030"),
                ]
            )
        ]
        self.assertEqual(expected, serializer.data)


class AirlineTestCase(TestCase):
    def test_save_convert_codes_to_uppercase(self):
        Airline(
            code="a3",
            name="Aegean",
            logo="a3.gif",
            country="gr",
            alliance="star",
        ).save()

        serializer = AirlineSerializer(Airline.objects.all(), many=True)
        expected = [
            OrderedDict(
                [
                    ("id", 1),
                    ("code", "A3"),
                    ("name", "Aegean"),
                    ("lc_name", ""),
                    ("logo", "a3.gif"),
                    ("country", "GR"),
                    ("alliance", "star"),
                ]
            )
        ]

        self.assertEqual(expected, serializer.data)


class AirportTestCase(TestCase):
    def test_save_convert_codes_to_uppercase(self):
        Airport(
            code="ath",
            name="Eleutherios Venizelos",
            parent_code="nOp",
            country="gr",
            city="Athens",
            longitude=23.946486,
            latitude=37.93635,
            train_station=False,
            bus_station=False,
            active=True,
            timezone="Europe / Athens",
        ).save()

        serializer = AirportSerializer(Airport.objects.all(), many=True)
        expected = [
            OrderedDict(
                [
                    ("id", 1),
                    ("code", "ATH"),
                    ("name", "Eleutherios Venizelos"),
                    ("parent_code", "NOP"),
                    ("country", "GR"),
                    ("city", "Athens"),
                    ("longitude", "23.946486"),
                    ("latitude", "37.93635"),
                    ("train_station", False),
                    ("bus_station", False),
                    ("active", True),
                    ("timezone", "Europe / Athens"),
                ]
            )
        ]

        self.assertEqual(expected, serializer.data)
