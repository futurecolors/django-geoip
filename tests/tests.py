# -*- coding: utf-8 -*-
from unittest import TestCase
from zipfile import ZipFile
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

    @patch('urllib2.urlopen')
    def test_download_unpack(self, mock):
        self.opener = mock.return_value
        self.opener.read.return_value = open('tests/tests.zip')

        result = Command()._download_unpack_archive()

        self.opener.read.assert_called_once_with()
        self.assertTrue(type(result), ZipFile)

    @patch('urllib2.urlopen')
    def test_download_exception(self, mock):
        mock.side_effect = urllib2.URLError('Response timeout')

        self.assertRaises(urllib2.URLError, Command()._download_unpack_archive)