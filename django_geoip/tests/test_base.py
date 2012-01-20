# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse

from django_any.models import any_model
from django_geoip.base import LocationStorage, Locator
from django_geoip.models import IpRange
from django_geoip.tests import RequestFactory, unittest
from test_app.models import MyCustomLocation

from mock import patch, Mock


@unittest.skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class LocationStorageTest(unittest.TestCase):

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

    def test_should_not_update_cookie_if_cookie_is_none(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = None
        storage = LocationStorage(request=self.request, response=HttpResponse())
        storage.value = None
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
        storage._do_set(10)
        expected = 'Set-Cookie: geoip_location_id=10; expires=Tue, 20-Nov-2328 17:46:39 GMT;'
        self.assertTrue(base_response.cookies[settings.GEOIP_COOKIE_NAME].output().startswith(expected))


@unittest.skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class LocatorTest(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        self.location_model_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
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

    @patch('test_app.models.MyCustomLocation.get_by_ip_range')
    @patch('test_app.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_doesnotexists(self, mock_get_default_location, mock_get_by_ip_range):
        mock_get_by_ip_range.side_effect = MyCustomLocation.DoesNotExist
        self.locator._get_corresponding_location(range)
        mock_get_by_ip_range.assert_called_once_with(range)
        mock_get_default_location.assert_called_once()

    @patch('test_app.models.MyCustomLocation.get_by_ip_range')
    @patch('test_app.models.MyCustomLocation.get_default_location')
    def test_get_corresponding_location_ok(self, mock_get_default_location, mock_get_by_ip_range):
        range = any_model(IpRange)
        self.locator._get_corresponding_location(range)
        mock_get_by_ip_range.assert_called_once_with(range)
        self.assertFalse(mock_get_default_location.called)

    @patch('django_geoip.base.Locator._get_cached_location')
    def test_locate_from_cache(self, mock_cached):
        self.assertEqual(self.locator.locate(), mock_cached.return_value)

    @patch('django_geoip.base.Locator._get_cached_location')
    @patch('django_geoip.base.Locator._get_corresponding_location')
    def test_locate_not_cached(self, mock_corresponding, mock_cached):
        mock_cached.return_value = None
        self.assertEqual(self.locator.locate(), mock_corresponding.return_value)