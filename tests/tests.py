# -*- coding: utf-8 -*-
from unittest import TestCase
from zipfile import ZipFile
from django.conf import settings
from django_any.models import any_model
from mock import patch
import urllib2
from django_geoip.management.commands.ipgeobase_update import Command
from django_geoip.models import IpRange, Country, Region, City

class IpRangeTest(TestCase):

    def test_manager(self):
        range_contains = any_model(IpRange, start_ip=3568355840, end_ip=3568355843)
        range_not_contains = any_model(IpRange, start_ip=3568355844, end_ip=3568355851)

        ip_range = IpRange.objects.by_ip('212.176.202.2')
        self.assertEqual(ip_range, range_contains)

        self.assertRaises(IpRange.DoesNotExist, IpRange.objects.by_ip, '127.0.0.1')
        #TODO Test for overlapping ranges

class DowloadTest(TestCase):
    IPGEOBASE_ZIP_FILE_PATH = 'tests/tests.zip'
    IPGEOBASE_MOCK_URL = 'http://futurecolors/mock.zip'

    @patch('urllib2.urlopen')
    def test_download_unpack(self, mock):
        self.opener = mock.return_value
        self.opener.read.return_value = open(self.IPGEOBASE_ZIP_FILE_PATH)

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
    def test_convert_fileline_to_dict(self):
        check_against_dict = {'city_id': u'1',
                              'city_name': u'Хмельницкий',
                              'region_name': u'Хмельницкая область',
                              'district_name': u'Центральная Украина',
                              'lat': u'49.416668',
                              'lng': u'27.000000'
                              }

        command = Command()
        generator = command._line_to_dict(file=open('tests/cities.txt'),
                                          field_names=settings.IPGEOBASE_CITIES_FIELDS)
        result = generator.next()
        self.assertEqual(result, check_against_dict)

    def test_convert_fileline_to_dict(self):
        check_against_dict = {'city_id': u'1',
                              'city_name': u'Хмельницкий',
                              'region_name': u'Хмельницкая область',
                              'district_name': u'Центральная Украина',
                              'lat': u'49.416668',
                              'lng': u'27.000000'
                              }

        command = Command()
        generator = command._line_to_dict(file=open('tests/cities.txt'),
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
            'countries': {u'FR', u'UA', u'RU'},
            'city_country_mapping': {'2176': u'RU', '1': u'UA'}
        }
        command = Command()
        cidr_info = command._process_cidr_file(open('tests/cidr_optim.txt'))

        self.assertEqual(cidr_info['city_country_mapping'], check_against['city_country_mapping'])
        self.assertEqual(cidr_info['countries'], check_against['countries'])
        self.assertEqual(cidr_info['cidr'], check_against['cidr'])


    def test_process_cities_file(self):
        city_country_mapping = {'1': u'UA', '1057': u'RU', '2176': u'RU'}

        check_against = {
            'cities': [
                {'region__name': u'Хмельницкая область', 'name': u'Хмельницкий', 'id': u'1'},
                {'region__name': u'Кемеровская область', 'name': u'Березовский', 'id': u'1057'},
                {'region__name': u'Ханты-Мансийский автономный округ', 'name': u'Мегион', 'id': u'2176'},
            ],
            'regions': [
                {'name':  u'Хмельницкая область', 'country__code': u'UA'},
                {'name':  u'Кемеровская область', 'country__code': u'RU'},
                {'name':  u'Ханты-Мансийский автономный округ', 'country__code': u'RU'},
            ]
        }

        command = Command()
        cities_info = command._process_cities_file(open('tests/cities.txt'), city_country_mapping)

        self.assertEqual(cities_info['cities'], check_against['cities'])
        self.assertEqual(cities_info['regions'], check_against['regions'])


class IpGeoBaseTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.countries = {u'FR', u'UA', u'RU'}
        self.regions = [{'name': u'Хмельницкая область', 'country': u'UA'},
                {'name': u'Кемеровская область', 'country': u'RU'},
                {'name': u'Ханты-Мансийский автономный округ', 'country': u'RU'}, ]
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
            'countries': {u'FR', u'UA', u'RU'},
            'city_country_mapping': {2176: u'RU', 1058: u'RU', 1057: u'RU', 1: u'UA'}
        }
        City.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()

    def test_update_geography_empty_data(self):
        command = Command()
        cities_info = command._update_geography(self.countries, self.regions, self.cities)

        self.assertEqual(set(Country.objects.all().values_list('code', flat=True)), self.countries)
        self.assertEqual(list(Region.objects.all().values('name', 'country')), self.regions)
        self.assertEqual(list(City.objects.all().values('name', 'id', 'region__name')), self.cities)

    def test_update_pre_existing_data(self):
        self.assertTrue(Country.objects.all().count() == 0)
        ua = Country.objects.create(name=u'UA', code=u'UA')
        ru = Country.objects.create(name=u'RU', code=u'RU')

        kemerovo = Region.objects.create(name=u'Кемеровская область', country=ru)
        City.objects.create(name=u'Березовский', id=1057, region=kemerovo)

        command = Command()
        cities_info = command._update_geography(self.countries, self.regions, self.cities)

        self.assertEqual(set(Country.objects.all().values_list('code', flat=True)), self.countries)
        self.assertItemsEqual(list(Region.objects.all().values('name', 'country')), self.regions)
        self.assertEqual(list(City.objects.all().values('name', 'id', 'region__name')), self.cities)

    def test_build_city_region_mapping(self):
        check_against_mapping = {
            1: 1,
            1057: 2,
            1058: 2,
            2176: 3,
        }
        for region in self.regions:
            Region.objects.create(name=region['name'], country_id=region['country'])
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
            Region.objects.create(name=region['name'], country_id=region['country'])
        for city in self.cities:
            region = Region.objects.get(name=city['region__name'])
            City.objects.create(id=city['id'], name=city['name'], region=region)
        command._update_cidr(self.cidr['cidr'])

        self.assertItemsEqual(IpRange.objects.all().values('start_ip', 'end_ip', 'country_id', 'city_id', 'region_id'),
            check_against_ranges)