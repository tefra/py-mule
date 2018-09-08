from django.db.models import QuerySet
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from resources.filters import MultiValueFilter
from resources.models import Country, Airline, Airport
from resources.serializers import (
    CountrySerializer,
    AirlineSerializer,
    AirportSerializer,
)


class ListViewSet(ListModelMixin, GenericViewSet):
    lookup_field = "code"
    filter_backends = (MultiValueFilter,)


class CountryViewSet(ListViewSet):
    queryset: QuerySet = Country.objects
    serializer_class = CountrySerializer
    lookup_value_regex = "[a-z]{2}"


class AirportViewSet(ListViewSet):
    queryset: QuerySet = Airport.objects
    serializer_class = AirportSerializer
    lookup_value_regex = "[a-z]{3}"


class AirlineViewSet(ListViewSet):
    queryset: QuerySet = Airline.objects
    serializer_class = AirlineSerializer
    lookup_value_regex = "[a-z0-9]{2}"
