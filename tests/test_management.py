# coding: utf-8
from __future__ import unicode_literals
import io
import os

import requests
from mock import patch
from decimal import Decimal

from django.test import TestCase
from django.conf import settings
from django_geoip import compat

from django_geoip.management.ipgeobase import IpGeobase
from django_geoip.models import City, Region, Country, IpRange


TEST_STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))


class DowloadTest(TestCase):
    IPGEOBASE_ZIP_FILE_PATH = 'tests.zip'
    IPGEOBASE_MOCK_URL = 'http://futurecolors/mock.zip'

    @patch.object(requests, 'get')
    def test_download_unpack(self, mock):
        self.opener = mock.return_value
        self.opener.content = io.open(os.path.join(TEST_STATIC_DIR, self.IPGEOBASE_ZIP_FILE_PATH),
                                                   mode='rb').read()

        result = IpGeobase()._download_extract_archive(url=self.IPGEOBASE_MOCK_URL)

        mock.assert_called_once_with(self.IPGEOBASE_MOCK_URL)
        self.assertEqual(len(result), 2)
        self.assertTrue(result['cities'].endswith(settings.IPGEOBASE_CITIES_FILENAME))
        self.assertTrue(result['cidr'].endswith(settings.IPGEOBASE_CIDR_FILENAME))

    @patch.object(requests, 'get')
    def test_download_exception(self, mock):
        mock.side_effect = requests.exceptions.Timeout('Response timeout')
        self.assertRaises(requests.exceptions.Timeout, IpGeobase()._download_extract_archive, self.IPGEOBASE_MOCK_URL)


class ConvertTest(TestCase):
    maxDiff = None

    def test_convert_fileline_to_dict(self):
        check_against_dict = {
            'city_id': '1',
            'city_name': 'Хмельницкий',
            'region_name': 'Хмельницкая область',
            'district_name': 'Центральная Украина',
            'latitude': '49.416668',
            'longitude': '27.000000'
        }

        backend = IpGeobase()
        generator = backend._line_to_dict(
            file=io.open(os.path.join(TEST_STATIC_DIR, 'cities.txt'), encoding=settings.IPGEOBASE_FILE_ENCODING),
            field_names=settings.IPGEOBASE_CITIES_FIELDS)
        result = compat.advance_iterator(generator)
        self.assertEqual(result, check_against_dict)

    def test_process_cidr_file(self):
        check_against = {
            'cidr': [
                    {'start_ip': '33554432', 'end_ip': '34603007', 'country_id': 'FR', 'city_id': None},
                    {'start_ip': '37249024', 'end_ip': '37251071', 'country_id': 'UA', 'city_id': '1'},
                    {'start_ip': '37355520', 'end_ip': '37392639', 'country_id': 'RU', 'city_id': '2176'},
            ],
            'countries': set(['FR', 'UA', 'RU']),
            'city_country_mapping': {'2176': 'RU', '1': 'UA'}
        }
        backend = IpGeobase()
        cidr_info = backend._process_cidr_file(open(os.path.join(TEST_STATIC_DIR, 'cidr_optim.txt')))

        self.assertEqual(cidr_info['city_country_mapping'], check_against['city_country_mapping'])
        self.assertEqual(cidr_info['countries'], check_against['countries'])
        self.assertEqual(cidr_info['cidr'], check_against['cidr'])

    @patch.object(settings, 'IPGEOBASE_ALLOWED_COUNTRIES', ['RU', 'UA'])
    def test_process_cidr_file_with_allowed_countries(self):
        check_against = {
            'cidr': [
                    {'start_ip': '37249024', 'end_ip': '37251071', 'country_id': 'UA', 'city_id': '1'},
                    {'start_ip': '37355520', 'end_ip': '37392639', 'country_id': 'RU', 'city_id': '2176'},
            ],
            'countries': set(['UA', 'RU']),
            'city_country_mapping': {'2176': 'RU', '1': 'UA'}
        }
        backend = IpGeobase()
        cidr_info = backend._process_cidr_file(open(os.path.join(TEST_STATIC_DIR, 'cidr_optim.txt')))

        self.assertEqual(cidr_info['city_country_mapping'], check_against['city_country_mapping'])
        self.assertEqual(cidr_info['countries'], check_against['countries'])
        self.assertEqual(cidr_info['cidr'], check_against['cidr'])

    def test_process_cities_file(self):
        city_country_mapping = {'1': 'UA', '1057': 'RU', '2176': 'RU'}

        check_against = {
            'cities': [
                    {'region__name': 'Хмельницкая область', 'name': 'Хмельницкий',
                     'id': '1', 'latitude': Decimal('49.416668'), 'longitude': Decimal('27.000000')},
                    {'region__name': 'Кемеровская область', 'name': 'Березовский',
                     'id': '1057', 'latitude': Decimal('55.572479'), 'longitude': Decimal('86.192734')},
                    {'region__name': 'Ханты-Мансийский автономный округ', 'name': 'Мегион',
                     'id': '2176', 'latitude': Decimal('61.050400'), 'longitude': Decimal('76.113472')},
            ],
            'regions': [
                    {'name':  'Хмельницкая область', 'country__code': 'UA'},
                    {'name':  'Кемеровская область', 'country__code': 'RU'},
                    {'name':  'Ханты-Мансийский автономный округ', 'country__code': 'RU'},
            ]
        }

        backend = IpGeobase()
        cities_info = backend._process_cities_file(io.open(os.path.join(TEST_STATIC_DIR, 'cities.txt'),
                                                   encoding=settings.IPGEOBASE_FILE_ENCODING), city_country_mapping)

        self.assertEqual(cities_info['cities'], check_against['cities'])
        self.assertEqual(cities_info['regions'], check_against['regions'])

    @patch.object(settings, 'IPGEOBASE_ALLOWED_COUNTRIES', ['RU'])
    def test_process_cities_file_with_allowed_countries(self):
        city_country_mapping = {'1': 'UA', '1057': 'RU', '2176': 'RU'}

        check_against = {
            'cities': [
                    {'region__name': 'Кемеровская область', 'name': 'Березовский',
                     'id': '1057', 'longitude': Decimal('86.192734'), 'latitude': Decimal('55.572479')},
                    {'region__name': 'Ханты-Мансийский автономный округ', 'name': 'Мегион',
                     'id': '2176', 'longitude': Decimal('76.113472'), 'latitude': Decimal('61.050400')},
            ],
            'regions': [
                    {'name':  'Кемеровская область', 'country__code': 'RU'},
                    {'name':  'Ханты-Мансийский автономный округ', 'country__code': 'RU'},
            ]
        }

        backend = IpGeobase()
        cities_info = backend._process_cities_file(io.open(os.path.join(TEST_STATIC_DIR, 'cities.txt'),
                                                   encoding=settings.IPGEOBASE_FILE_ENCODING), city_country_mapping)

        self.assertEqual(cities_info['cities'], check_against['cities'])
        self.assertEqual(cities_info['regions'], check_against['regions'])

class IpGeoBaseTest(TestCase):
    maxDiff = None

    def assertCountEqual(self, first, second, msg=None):
        if compat.PY3:
            return super(IpGeoBaseTest, self).assertCountEqual(first, second, msg)
        else:
            return super(IpGeoBaseTest, self).assertItemsEqual(first, second, msg)

    def setUp(self):
        self.countries = set(['FR', 'UA', 'RU'])
        self.regions = [{'name': 'Хмельницкая область', 'country__code': 'UA'},
                {'name': 'Кемеровская область', 'country__code': 'RU'},
                {'name': 'Ханты-Мансийский автономный округ', 'country__code': 'RU'}, ]
        self.cities = [{'region__name': 'Хмельницкая область', 'name': 'Хмельницкий', 'id': 1},
                {'region__name': 'Кемеровская область', 'name': 'Березовский', 'id': 1057},
                {'region__name': 'Кемеровская область', 'name': 'Кемерово', 'id': 1058},
                {'region__name': 'Ханты-Мансийский автономный округ', 'name': 'Мегион', 'id': 2176}, ]
        self.cidr = {
            'cidr': [
                    {'start_ip': '33554432', 'end_ip': '34603007','country_id': 'FR', 'city_id': None},
                    {'start_ip': '37249024', 'end_ip': '37251071','country_id': 'UA', 'city_id': '1'},
                    {'start_ip': '37355520', 'end_ip': '37392639','country_id': 'RU', 'city_id': '2176'},
            ],
            'countries': set(['FR', 'UA', 'RU']),
            'city_country_mapping': {2176: 'RU', 1058: 'RU', 1057: 'RU', 1: 'UA'}
        }
        City.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()

    def test_update_geography_empty_data(self):
        command = IpGeobase()
        cities_info = command._update_geography(self.countries, self.regions, self.cities)

        check_against_countries = [
            {'code':'FR', 'name':'France'},
            {'code':'UA', 'name':'Ukraine'},
            {'code':'RU', 'name':'Russian Federation'}
        ]

        self.assertCountEqual(Country.objects.all().values('code', 'name'), check_against_countries)
        self.assertEqual(list(Region.objects.all().values('name', 'country__code')), self.regions)
        self.assertEqual(list(City.objects.all().values('name', 'id', 'region__name')), self.cities)

    def test_update_pre_existing_data(self):
        self.assertTrue(Country.objects.all().count() == 0)
        ua = Country.objects.create(name='Ukraine', code='UA')
        ru = Country.objects.create(name='Russia', code='RU')

        kemerovo = Region.objects.create(name='Кемеровская область', country=ru)
        City.objects.create(name='Березовский', id=1057, region=kemerovo)

        backend = IpGeobase()
        backend._update_geography(self.countries, self.regions, self.cities)

        self.assertEqual(set(Country.objects.all().values_list('code', flat=True)), self.countries)
        self.assertCountEqual(list(Region.objects.all().values('name', 'country__code')), self.regions)
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

        backend = IpGeobase()
        mapping = backend._build_city_region_mapping()

        self.assertCountEqual(mapping, check_against_mapping)


    def test_update_cidr(self):
        check_against_ranges = [
            {'start_ip': 33554432, 'end_ip': 34603007, 'country_id': 'FR', 'city_id': None, 'region_id': None},
            {'start_ip': 37249024, 'end_ip': 37251071, 'country_id': 'UA', 'city_id': 1, 'region_id': 1},
            {'start_ip': 37355520, 'end_ip': 37392639, 'country_id': 'RU', 'city_id': 2176,'region_id': 3},
        ]

        backend = IpGeobase()
        for region in self.regions:
            Region.objects.create(name=region['name'], country_id=region['country__code'])
        for city in self.cities:
            region = Region.objects.get(name=city['region__name'])
            City.objects.create(id=city['id'], name=city['name'], region=region)
        backend._update_cidr(self.cidr)

        self.assertCountEqual(IpRange.objects.all().values('start_ip', 'end_ip', 'country_id', 'city_id', 'region_id'),
                              check_against_ranges)
