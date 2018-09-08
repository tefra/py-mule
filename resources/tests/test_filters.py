from django.test import TestCase
from rest_framework import generics, status
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APIRequestFactory

from resources.filters import MultiValueFilter
from resources.models import Airline

factory = APIRequestFactory()


class AirlineSerializer(ModelSerializer):
    class Meta:
        model = Airline
        fields = ("code",)


class MultiValueListView(generics.ListAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    filter_backends = (MultiValueFilter,)
    lookup_field = "code"


class MultiValueFilterTests(TestCase):
    def setUp(self):
        Airline(code="A3").save()
        Airline(code="FR").save()

    def test_filter_queryset(self):
        view = MultiValueListView.as_view()
        request = factory.get("/", {"code": ["a3", "fr", "no"]})
        response = view(request)
        self.assertEqual([{"code": "A3"}, {"code": "FR"}], response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_filter_queryset_with_no_values(self):
        view = MultiValueListView.as_view()
        request = factory.get("/")
        response = view(request)
        self.assertEqual({"detail": "Malformed request."}, response.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
