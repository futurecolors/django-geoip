# -*- coding: utf-8 -*-
import struct
import socket

from django.test import TestCase
from django_geoip.models import IpRange, GeoLocationFacade

from tests import factory
from tests.factory import create_ip_range


class IpRangeTest(TestCase):

    def setUp(self):
        self.range_contains = create_ip_range(start_ip=3568355840, end_ip=3568355843)
        self.range_not_contains = create_ip_range(start_ip=3568355844, end_ip=3568355851)

    def test_manager(self):
        ip_range = IpRange.objects.by_ip('212.176.202.2')
        self.assertEqual(ip_range, self.range_contains)
        self.assertRaises(IpRange.DoesNotExist, IpRange.objects.by_ip, '127.0.0.1')

    def test_invalid_ip(self):
        self.assertRaises(IpRange.DoesNotExist, IpRange.objects.by_ip, 'wtf')

    def test_relations(self):
        self.country = factory.any_country()
        self.region = factory.any_region(country=self.country)
        self.city = factory.any_city(region=self.region)
        range = create_ip_range(start_ip=struct.unpack('!L', socket.inet_aton('43.123.56.0'))[0],
                                end_ip=struct.unpack('!L', socket.inet_aton('43.123.56.255'))[0],
                                city=self.city, region=self.region, country=self.country)

        ip_range = IpRange.objects.by_ip('43.123.56.12')
        self.assertEqual(ip_range.city, self.city)
        self.assertEqual(ip_range.city.region, self.region)
        self.assertEqual(ip_range.city.region.country, self.country)


class GeoFacadeTest(TestCase):

    def test_bad_subclass_doesnt_implement(self):

        class MyFacade(GeoLocationFacade):

            @classmethod
            def get_by_ip_range(cls, ip_range):
                return None

        self.assertRaises(TypeError, MyFacade)

    def test_facade_is_abstract_django_model(self):
        facade = GeoLocationFacade
        self.assertEqual(facade._meta.abstract, True)