# -*- coding: utf-8 -*-
from datetime import datetime
import sys
import socket
import urllib2
import struct
import os
import django
from django.core.urlresolvers import get_mod_func
from unittest2.case import expectedFailure
import django_geoip
from decimal import Decimal
from django.http import HttpResponse
from django_geoip.base import Locator, LocationStorage
from django_geoip.utils import get_class
from models import MyCustomLocation

try:
    from django.test.client import RequestFactory
except ImportError:
    RequestFactory = None
from django_any.test import Client
from django_geoip import middleware

try:
    from unittest2 import TestCase, skipIf
except ImportError:
    if sys.version_info >= (2,7):
        # unittest2 features are native in Python 2.7
        from unittest import TestCase, skipIf
        from unittest.case import expectedFailure
    else:
        raise

from mock import patch, Mock
from django.conf import settings
from django_any.models import any_model

from django_geoip.management.commands.ipgeobase_update import Command
from django_geoip.models import IpRange, Country, Region, City, inet_aton

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class IpRangeTest(TestCase):

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

class DowloadTest(TestCase):
    IPGEOBASE_ZIP_FILE_PATH = 'tests.zip'
    IPGEOBASE_MOCK_URL = 'http://futurecolors/mock.zip'

    @patch('urllib2.urlopen')
    def test_download_unpack(self, mock):
        self.opener = mock.return_value
        self.opener.read.return_value = open(os.path.join(BASE_DIR, self.IPGEOBASE_ZIP_FILE_PATH)).read()

        result = Command()._download_extract_archive(url=self.IPGEOBASE_MOCK_URL)

        mock.assert_called_once_with(self.IPGEOBASE_MOCK_URL)
        self.opener.read.assert_called_once_with()
        self.assertEqual(len(result), 2)
        self.assertTrue(result['cities'].endswith(settings.IPGEOBASE_CITIES_FILENAME))
        self.assertTrue(result['cidr'].endswith(settings.IPGEOBASE_CIDR_FILENAME))

    @patch('urllib2.urlopen')
    def test_download_exception(self, mock):
        mock.side_effect = urllib2.URLError('Response timeout')
        self.assertRaises(urllib2.URLError, Command()._download_extract_archive, self.IPGEOBASE_MOCK_URL)


class ConvertTest(TestCase):
    maxDiff = None

    def test_convert_fileline_to_dict(self):
        check_against_dict = {'city_id': u'1',
                              'city_name': u'Хмельницкий',
                              'region_name': u'Хмельницкая область',
                              'district_name': u'Центральная Украина',
                              'lat': u'49.416668',
                              'lng': u'27.000000'
                              }

        command = Command()
        generator = command._line_to_dict(file=open(os.path.join(BASE_DIR, 'cities.txt')),
                                          field_names=settings.IPGEOBASE_CITIES_FIELDS)
        result = generator.next()
        self.assertEqual(result, check_against_dict)

    def test_convert_fileline_to_dict(self):
        check_against_dict = {'city_id': u'1',
                              'city_name': u'Хмельницкий',
                              'region_name': u'Хмельницкая область',
                              'district_name': u'Центральная Украина',
                              'longitude': u'49.416668',
                              'latitude': u'27.000000'
                              }

        command = Command()
        generator = command._line_to_dict(file=open(os.path.join(BASE_DIR, 'cities.txt')),
                                          field_names=settings.IPGEOBASE_CITIES_FIELDS)
        result = generator.next()
        self.assertEqual(result, check_against_dict)

    def test_process_cidr_file(self):
        check_against = {
            'cidr': [
                {'start_ip': '33554432', 'end_ip': '34603007','country_id': 'FR', 'city_id': None},
                {'start_ip': '37249024', 'end_ip': '37251071','country_id': 'UA', 'city_id': '1'},
                {'start_ip': '37355520', 'end_ip': '37392639','country_id': 'RU', 'city_id': '2176'},
            ],
            'countries': set([u'FR', u'UA', u'RU']),
            'city_country_mapping': {'2176': u'RU', '1': u'UA'}
        }
        command = Command()
        cidr_info = command._process_cidr_file(open(os.path.join(BASE_DIR, 'cidr_optim.txt')))

        self.assertEqual(cidr_info['city_country_mapping'], check_against['city_country_mapping'])
        self.assertEqual(cidr_info['countries'], check_against['countries'])
        self.assertEqual(cidr_info['cidr'], check_against['cidr'])


    def test_process_cities_file(self):
        city_country_mapping = {'1': u'UA', '1057': u'RU', '2176': u'RU'}

        check_against = {
            'cities': [
                {'region__name': u'Хмельницкая область', 'name': u'Хмельницкий',
                 'id': u'1', 'longitude': Decimal('49.416668'), 'latitude': Decimal('27.000000')},
                {'region__name': u'Кемеровская область', 'name': u'Березовский',
                 'id': u'1057', 'longitude': Decimal('55.572479'), 'latitude': Decimal('86.192734')},
                {'region__name': u'Ханты-Мансийский автономный округ', 'name': u'Мегион',
                 'id': u'2176', 'longitude': Decimal('61.050400'), 'latitude': Decimal('76.113472')},
            ],
            'regions': [
                {'name':  u'Хмельницкая область', 'country__code': u'UA'},
                {'name':  u'Кемеровская область', 'country__code': u'RU'},
                {'name':  u'Ханты-Мансийский автономный округ', 'country__code': u'RU'},
            ]
        }

        command = Command()
        cities_info = command._process_cities_file(open(os.path.join(BASE_DIR, 'cities.txt')), city_country_mapping)

        self.assertEqual(cities_info['cities'], check_against['cities'])
        self.assertEqual(cities_info['regions'], check_against['regions'])


class IpGeoBaseTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.countries = set([u'FR', u'UA', u'RU'])
        self.regions = [{'name': u'Хмельницкая область', 'country__code': u'UA'},
                {'name': u'Кемеровская область', 'country__code': u'RU'},
                {'name': u'Ханты-Мансийский автономный округ', 'country__code': u'RU'}, ]
        self.cities = [{'region__name': u'Хмельницкая область', 'name': u'Хмельницкий', 'id': 1},
                {'region__name': u'Кемеровская область', 'name': u'Березовский', 'id': 1057},
                {'region__name': u'Кемеровская область', 'name': u'Кемерово', 'id': 1058},
                {'region__name': u'Ханты-Мансийский автономный округ', 'name': u'Мегион', 'id': 2176}, ]
        self.cidr = {
            'cidr': [
                {'start_ip': '33554432', 'end_ip': '34603007','country_id': 'FR', 'city_id': None},
                {'start_ip': '37249024', 'end_ip': '37251071','country_id': 'UA', 'city_id': '1'},
                {'start_ip': '37355520', 'end_ip': '37392639','country_id': 'RU', 'city_id': '2176'},
            ],
            'countries': set([u'FR', u'UA', u'RU']),
            'city_country_mapping': {2176: u'RU', 1058: u'RU', 1057: u'RU', 1: u'UA'}
        }
        City.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()

    def test_update_geography_empty_data(self):
        command = Command()
        cities_info = command._update_geography(self.countries, self.regions, self.cities)

        self.assertEqual(set(Country.objects.all().values_list('code', flat=True)), self.countries)
        self.assertEqual(list(Region.objects.all().values('name', 'country__code')), self.regions)
        self.assertEqual(list(City.objects.all().values('name', 'id', 'region__name')), self.cities)

    def test_update_pre_existing_data(self):
        self.assertTrue(Country.objects.all().count() == 0)
        ua = Country.objects.create(name=u'UA', code=u'UA')
        ru = Country.objects.create(name=u'RU', code=u'RU')

        kemerovo = Region.objects.create(name=u'Кемеровская область', country=ru)
        City.objects.create(name=u'Березовский', id=1057, region=kemerovo)

        command = Command()
        command._update_geography(self.countries, self.regions, self.cities)

        self.assertEqual(set(Country.objects.all().values_list('code', flat=True)), self.countries)
        self.assertItemsEqual(list(Region.objects.all().values('name', 'country__code')), self.regions)
        self.assertEqual(list(City.objects.all().values('name', 'id', 'region__name')), self.cities)

    def test_build_city_region_mapping(self):
        check_against_mapping = {
            1: 1,
            1057: 2,
            1058: 2,
            2176: 3,
        }
        for region in self.regions:
            Region.objects.create(name=region['name'], country_id=region['country__code'])
        for city in self.cities:
            region = Region.objects.get(name=city['region__name'])
            City.objects.create(id=city['id'], name=city['name'], region=region)

        command = Command()
        mapping = command._build_city_region_mapping()

        self.assertEqual(mapping, check_against_mapping)


    def test_update_cidr(self):
        check_against_ranges = [
            {'start_ip': 33554432, 'end_ip': 34603007, 'country_id': 'FR', 'city_id': None, 'region_id': None},
            {'start_ip': 37249024, 'end_ip': 37251071, 'country_id': 'UA', 'city_id': 1, 'region_id': 1},
            {'start_ip': 37355520, 'end_ip': 37392639, 'country_id': 'RU', 'city_id': 2176,'region_id': 3},
        ]

        command = Command()
        for region in self.regions:
            Region.objects.create(name=region['name'], country_id=region['country__code'])
        for city in self.cities:
            region = Region.objects.get(name=city['region__name'])
            City.objects.create(id=city['id'], name=city['name'], region=region)
        command._update_cidr(self.cidr)

        self.assertItemsEqual(IpRange.objects.all().values('start_ip', 'end_ip', 'country_id', 'city_id', 'region_id'),
            check_against_ranges)


@skipIf(django.VERSION < (1, 3), "RequestFactory is avaliable from 1.3")
class MiddlewareTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.client = Client()
        self.factory = RequestFactory()
        self.request = self.factory.get('/', **{'REMOTE_ADDR': '6.6.6.6'})
        self.middleware = django_geoip.middleware.LocationMiddleware()

        self.get_location_patcher = patch.object(middleware, 'get_location')
        self.get_location_patcher.start()
        self.get_location_mock = self.get_location_patcher.start()

    def tearDown(self, *args, **kwargs):
        self.get_location_patcher.stop()

    def test_get_location_lazy(self):
        self.client.get('/')
        self.assertEqual(self.get_location_mock.call_count, 0)

    def test_process_request(self):
        self.get_location_mock.return_value = None
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.location, None)
        self.assertEqual(self.get_location_mock.call_count, 1)

    @patch('django_geoip.base.LocationStorage.set')
    @patch.object(LocationStorage, '__init__')
    def test_process_response(self, mock, mock_location_set):
        mock.return_value = None
        base_response = HttpResponse()
        self.get_location_mock.return_value = mycity = any_model(City)
        self.middleware.process_request(self.request)
        self.middleware.process_response(self.request, base_response)
        mock.assert_called_once_with(request=self.request, response=base_response)
        mock_location_set.assert_called_once_with(value=mycity.id)


class LocationStorageTest(TestCase):

    def setUp(self, *args, **kwargs):
        self.request = RequestFactory().get('/')
        self.request.location = Mock()

    def test_should_not_update_cookie_if_no_location_in_request(self):
        storage = LocationStorage(request=RequestFactory().get('/'), response=HttpResponse())
        self.assertFalse(storage._should_update_cookie())

    def test_should_update_cookie_if_cookie_doesnt_exist(self):
        storage = LocationStorage(request=self.request, response=HttpResponse())
        self.assertTrue(storage._should_update_cookie())

    def test_should_not_update_cookie_if_cookie_is_fresh(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = 10
        storage = LocationStorage(request=self.request, response=HttpResponse())
        storage.value = 10
        self.assertFalse(storage._should_update_cookie())

    def test_should_update_cookie_if_cookie_is_obsolete(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = 42
        storage = LocationStorage(request=self.request, response=HttpResponse())
        storage.value = 10
        self.assertTrue(storage._should_update_cookie())

    @patch('django_geoip.base.datetime')
    def test_do_set(self, mock):
        mock.now.return_value = datetime(2012, 1, 1, 0, 0, 0)
        base_response = HttpResponse()
        storage = LocationStorage(request=self.request, response=base_response)
        storage.value = 10
        storage._do_set()
        expected = 'Set-Cookie: geoip_location_id=10; expires=Tue, 20-Nov-2328 17:46:39 GMT;'
        self.assertTrue(base_response.cookies[settings.GEOIP_COOKIE_NAME].output().startswith(expected))


@skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class GetLocation(TestCase):

    def setUp(self, *args, **kwargs):
        self.client = Client()
        self.factory = RequestFactory()

        any_model(MyCustomLocation, pk=1, city__name='city1')
        self.my_location = any_model(MyCustomLocation, id=200, city__name='city200')

    def tearDown(self, *args, **kwargs):
        City.objects.all().delete()

    @patch.object(settings, 'GEOIP_LOCATION_MODEL', 'tests.models.MyCustomLocation')
    def test_get_cached_location_ok(self):
        self.factory.cookies[settings.GEOIP_COOKIE_NAME] = 200
        request = self.factory.get('/')
        self.assertEqual(Locator(request)._get_cached_location(), self.my_location)

    @patch.object(settings, 'GEOIP_LOCATION_MODEL', 'tests.models.MyCustomLocation')
    def test_get_cached_location_none(self):
        request = self.factory.get('/')
        self.assertEqual(Locator(request)._get_cached_location(), None)


class UtilsTest(TestCase):
    def test_get_mod_func(self):
        test_hash = {
            'django.views.news.stories.story_detail': ('django.views.news.stories', 'story_detail'),
            'django': ('django', ''),
        }

        for klass, expected_result in test_hash.items():
            self.assertEqual(get_mod_func(klass), expected_result)

    @patch('django.contrib.sessions.backends.base.SessionBase')
    def test_get_class(self, SessionBase):
        """ FIXME: change to fake class"""
        test_hash = {
            'django.contrib.sessions.backends.base.SessionBase': SessionBase,
        }

        for class_string, expected_class_instance in test_hash.items():
            self.assertEqual(get_class(class_string), expected_class_instance)

        self.assertRaises(ImportError, get_class, 'django_geoip.fake')


class LocatorTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.location_model_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'tests.models.MyCustomLocation')
        self.location_model = self.location_model_patcher.start()

        self.locator = Locator(RequestFactory().get('/'))

    def tearDown(self):
        self.location_model_patcher.stop()

    def test_get_cached_location_none(self):
        self.assertEqual(self.locator._get_cached_location(), None)

        self.locator.request.COOKIES['geoip_location_id'] = 1
        self.assertEqual(self.locator._get_cached_location(), None)

    def test_get_cached_location_ok(self):
        location = any_model(MyCustomLocation)
        self.locator.request.COOKIES['geoip_location_id'] = location.id
        self.assertEqual(self.locator._get_cached_location(), location)

    @patch('django_geoip.base.Locator._get_real_ip')
    def test_get_ip_range_none(self, mock_get_ip):
        mock_get_ip.return_value = '1.2.3.4'
        self.assertEqual(self.locator._get_ip_range(), None)

    @patch('django_geoip.base.Locator._get_real_ip')
    @patch('django_geoip.models.IpRange.objects.by_ip')
    def test_get_ip_range_ok(self, by_ip, mock_get_ip):
        mock_get_ip.return_value = '1.2.3.4'

        self.assertEqual(self.locator._get_ip_range(), by_ip.return_value)
        by_ip.assert_called_once_with('1.2.3.4')

    @patch('tests.models.MyCustomLocation.get_by_ip_range')
    @patch('tests.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_doesnotexists(self, mock_get_default_location, mock_get_by_ip_range):
        mock_get_by_ip_range.side_effect = MyCustomLocation.DoesNotExist
        self.locator._get_corresponding_location(range)
        mock_get_by_ip_range.assert_called_once_with(range)
        mock_get_default_location.assert_called_once()

    @patch('tests.models.MyCustomLocation.get_by_ip_range')
    @patch('tests.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_ok(self, mock_get_default_location, mock_get_by_ip_range):
        range = any_model(IpRange)
        self.locator._get_corresponding_location(range)
        mock_get_by_ip_range.assert_called_once_with(range)
        self.assertFalse(mock_get_default_location.called)

    @patch('django_geoip.base.Locator._get_cached_location')
    def test_locate_from_cache(self, mock_cached):
        self.assertEqual(self.locator.locate(), mock_cached.return_value)

    @patch('django_geoip.base.Locator._get_cached_location')
    @patch('django_geoip.base.Locator._get_ip_range')
    @patch('django_geoip.base.Locator._get_corresponding_location')
    def test_locate_from_cache(self, mock_corresponding, mock_get_range, mock_cached):
        mock_cached.return_value = None
        self.assertEqual(self.locator.locate(), mock_corresponding.return_value)