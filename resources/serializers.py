from rest_framework.serializers import ModelSerializer

from resources.models import Country, Airline, Airport, Continent


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class AirportSerializer(ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class AirlineSerializer(ModelSerializer):
    class Meta:
        model = Airline
        fields = "__all__"


class Continent(ModelSerializer):
    class Meta:
        model = Continent
        fields = "__all__"
