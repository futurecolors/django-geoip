# -*- coding: utf-8 -*-
from django.conf import settings

from django_any.models import any_model
from django_geoip.base import  Locator
from django_geoip.models import IpRange
from django_geoip.tests import RequestFactory, unittest
from test_app.models import MyCustomLocation

from mock import patch, Mock


@unittest.skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class LocatorTest(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        self.location_model_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
        self.location_model = self.location_model_patcher.start()

        self.locator = Locator(RequestFactory().get('/'))

    def tearDown(self):
        self.location_model_patcher.stop()

    def test_get_stored_location_none(self):
        self.assertEqual(self.locator._get_stored_location(), None)

        self.locator.request.COOKIES['geoip_location_id'] = 1
        self.assertEqual(self.locator._get_stored_location(), None)

    def test_get_stored_location_ok(self):
        location = any_model(MyCustomLocation)
        self.locator.request.COOKIES['geoip_location_id'] = location.id
        self.assertEqual(self.locator._get_stored_location(), location)

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

    @patch('django_geoip.base.Locator._get_stored_location')
    def test_is_store_empty(self, mock_get_stored):
        mock_get_stored.return_value = None
        self.assertTrue(self.locator.is_store_empty())
        mock_get_stored.return_value = 1
        self.assertFalse(self.locator.is_store_empty())

    @patch('test_app.models.MyCustomLocation.get_by_ip_range')
    @patch('test_app.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_doesnotexists(self, mock_get_default_location, mock_get_by_ip_range):
        mock_get_by_ip_range.side_effect = MyCustomLocation.DoesNotExist
        ip_range = Mock()
        self.locator._get_corresponding_location(ip_range)
        mock_get_by_ip_range.assert_called_once_with(ip_range)
        mock_get_default_location.assert_called_once()

    @patch('test_app.models.MyCustomLocation.get_by_ip_range')
    @patch('test_app.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_exception(self, mock_get_default_location, mock_get_by_ip_range):
        mock_get_by_ip_range.side_effect = None
        ip_range = Mock()
        self.locator._get_corresponding_location(ip_range)
        mock_get_by_ip_range.assert_called_once_with(ip_range)
        mock_get_default_location.assert_called_once()

    @patch('test_app.models.MyCustomLocation.get_by_ip_range')
    @patch('test_app.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_ok(self, mock_get_default_location, mock_get_by_ip_range):
        range = any_model(IpRange)
        self.locator._get_corresponding_location(range)
        mock_get_by_ip_range.assert_called_once_with(range)
        self.assertFalse(mock_get_default_location.called)

    @patch('django_geoip.base.Locator._get_stored_location')
    def test_locate_from_stored(self, mock_stored):
        self.assertEqual(self.locator.locate(), mock_stored.return_value)

    @patch('django_geoip.base.Locator._get_stored_location')
    @patch('django_geoip.base.Locator._get_corresponding_location')
    def test_locate_not_stored(self, mock_corresponding, mock_stored):
        mock_stored.return_value = None
        self.assertEqual(self.locator.locate(), mock_corresponding.return_value)