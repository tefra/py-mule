from django.db.models import QuerySet
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from resources.filters import MultiValueFilter
from resources.models import Airline, Airport
from resources.serializers import AirlineSerializer, AirportSerializer


class ListViewSet(ListModelMixin, GenericViewSet):
    lookup_field = "code"
    filter_backends = (MultiValueFilter,)


class AirportViewSet(ListViewSet):
    queryset: QuerySet = Airport.objects
    serializer_class = AirportSerializer
    lookup_value_regex = "[A-Za-z]{3}"


class AirlineViewSet(ListViewSet):
    queryset: QuerySet = Airline.objects
    serializer_class = AirlineSerializer
    lookup_value_regex = "[A-Za-z0-9]{2}"
