# -*- coding: utf-8 -*-
import struct
import socket
from django_any.models import any_model
from django_geoip.models import IpRange, Region, Country, City
from django_geoip.tests import unittest

class IpRangeTest(unittest.TestCase):

    def setUp(self):
        self.range_contains = any_model(IpRange, start_ip=3568355840, end_ip=3568355843)
        self.range_not_contains = any_model(IpRange, start_ip=3568355844, end_ip=3568355851)

    def test_manager(self):
        ip_range = IpRange.objects.by_ip('212.176.202.2')
        self.assertEqual(ip_range, self.range_contains)
        self.assertRaises(IpRange.DoesNotExist, IpRange.objects.by_ip, '127.0.0.1')

    def test_relations(self):
        self.country = any_model(Country)
        self.region = any_model(Region, country=self.country)
        self.city = any_model(City, region=self.region)
        range = any_model(IpRange,
                          start_ip=struct.unpack('!L', socket.inet_aton('43.123.56.0'))[0],
                          end_ip=struct.unpack('!L', socket.inet_aton('43.123.56.255'))[0],
                          city=self.city, region=self.region, country=self.country)

        ip_range = IpRange.objects.by_ip('43.123.56.12')
        self.assertEqual(ip_range.city, self.city)
        self.assertEqual(ip_range.city.region, self.region)
        self.assertEqual(ip_range.city.region.country, self.country)