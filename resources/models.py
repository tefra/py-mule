from enum import Enum

from django.db import models

from mule.converters import upper


class Continent(Enum):
    AFRICA = "Africa"
    ASIA = "Asia"
    CARIBBEAN = "Caribbean"
    NORTH_AMERICA = "North America"
    CENTRAL_AMERICA = "Central America"
    SOUTH_AMERICA = "South America"
    OCEANIA = "Oceania"
    EUROPE = "Europe"

    @classmethod
    def choices(cls):
        return ((x.value, x.name) for x in Continent)

    def __str__(self):
        return self.value


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    iso_code = models.CharField(max_length=3, db_index=True)
    name = models.CharField(max_length=256)
    continent = models.CharField(max_length=256, choices=Continent.choices())
    dialingCode = models.CharField(max_length=6)

    def save(self, *args, **kwargs):
        self.code = upper(self.code)
        self.iso_code = upper(self.iso_code)
        super().save(*args, **kwargs)


class Airline(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=256)
    lc_name = models.CharField(max_length=256)
    logo = models.CharField(max_length=256)
    country = models.CharField(max_length=2)
    alliance = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        self.code = upper(self.code)
        self.country = upper(self.country)
        super().save(*args, **kwargs)


class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=256)
    parent_code = models.CharField(max_length=3, db_index=True)
    country = models.ForeignKey(
        Country, on_delete=None, to_field="code", null=True
    )
    city = models.CharField(max_length=256)
    longitude = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)
    train_station = models.BooleanField(default=False)
    bus_station = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    timezone = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        self.code = upper(self.code)
        self.parent_code = upper(self.parent_code)
        super().save(*args, **kwargs)
