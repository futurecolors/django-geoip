# -*- coding: utf-8 -*-
from django.db import models
from django_geoip.models import GeoLocationFascade, City

class MyCustomLocation(GeoLocationFascade):
    name = models.CharField(max_length=100)
    city = models.OneToOneField(City, related_name='my_custom_location')

    @classmethod
    def get_by_ip_range(cls, ip_range):
        return ip_range.city.my_custom_location

    @classmethod
    def get_default_location(cls):
        return cls.objects.get(pk=1)

    def __repr__(self):
        return 'MyCustomLocation(id={0}, city={1})'.format(self.pk, self.city.name)