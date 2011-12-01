# -*- coding: utf-8 -*-
from unittest import TestCase
from zipfile import ZipFile
from django.conf import settings
from django_any.models import any_model
from mock import patch
import urllib2
from django_geoip.management.commands.ipgeobase_update import Command
from django_geoip.models import IpRange

class IpRangeTest(TestCase):

    def test_manager(self):
        range_contains = any_model(IpRange, start_ip=3568355840, end_ip=3568355843)
        range_not_contains = any_model(IpRange, start_ip=3568355844, end_ip=3568355851)

        ip_range = IpRange.objects.by_ip('212.176.202.2')
        self.assertEqual(ip_range, range_contains)

        self.assertRaises(IpRange.DoesNotExist, IpRange.objects.by_ip, '127.0.0.1')
        #TODO Test for overlapping ranges

        
class IpGeoBaseTest(TestCase):
    maxDiff = None
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
                {'start_ip': '33554432', 'end_ip': '34603007','country_id': 'FR', 'city_id': '-'},
                {'start_ip': '37249024', 'end_ip': '37251071','country_id': 'UA', 'city_id': '414'},
                {'start_ip': '37355520', 'end_ip': '37392639','country_id': 'RU', 'city_id': '2097'},
            ],
            'countries': {u'FR', u'UA', u'RU'},
            'city_country_mapping': {'2097': u'RU', '414': u'UA'}
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
            ]
        }

        command = Command()
        cities_info = command._process_cities_file(open('tests/cities.txt'), city_country_mapping)

        self.assertEqual(cities_info['cities'], check_against['cities'])

