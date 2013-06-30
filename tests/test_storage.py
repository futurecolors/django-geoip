# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, HttpRequest
from mock import patch, Mock
from django_geoip.storage import LocationCookieStorage, LocationDummyStorage, BaseLocationStorage
from test_app.models import MyCustomLocation
from tests.factory import create_custom_location


class BaseLocationStorageTest(TestCase):

    def setUp(self):
        self.settings_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
        self.settings_patcher.start()

        self.storage = BaseLocationStorage(request=HttpRequest(), response=HttpResponse())

    def tearDown(self):
        self.settings_patcher.stop()

    def test_validate_location(self):
        self.assertFalse(self.storage._validate_location(None))
        self.assertFalse(self.storage._validate_location(Mock()))

        location = create_custom_location(MyCustomLocation)
        self.assertTrue(self.storage._validate_location(location))


class LocationCookieStorageTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.location = Mock()

    def test_should_not_update_cookie_if_no_location_in_request(self):
        storage = LocationCookieStorage(request=HttpRequest(), response=HttpResponse())
        self.assertFalse(storage._should_update_cookie(new_value=10))

    def test_should_update_cookie_if_cookie_doesnt_exist(self):
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertTrue(storage._should_update_cookie(new_value=10))

    def test_should_not_update_cookie_if_cookie_is_none(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = settings.GEOIP_LOCATION_EMPTY_VALUE
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertFalse(storage._should_update_cookie(new_value=settings.GEOIP_LOCATION_EMPTY_VALUE))

    def test_should_not_update_cookie_if_cookie_is_none(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = None
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertFalse(storage._should_update_cookie(new_value=None))

    def test_should_not_update_cookie_if_cookie_is_fresh(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = 10
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertFalse(storage._should_update_cookie(new_value=10))

    def test_should_update_cookie_if_cookie_is_obsolete(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = 42
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertTrue(storage._should_update_cookie(new_value=10))

    def test_should_update_cookie_if_cookie_is_empty_value(self):
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertTrue(storage._should_update_cookie(new_value=settings.GEOIP_LOCATION_EMPTY_VALUE))

    def test_validate_location_if_cookies_is_empty_value(self):
        value = settings.GEOIP_LOCATION_EMPTY_VALUE
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertTrue(storage._validate_location(location=value))

    @patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
    def test_malicious_cookie_is_no_problem(self):
        self.request.COOKIES[settings.GEOIP_COOKIE_NAME] = "wtf"
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage.get(), None)

    @patch('django_geoip.storage.datetime')
    def test_do_set(self, mock):
        mock.utcnow.return_value = datetime(2030, 1, 1, 0, 0, 0)
        base_response = HttpResponse()
        storage = LocationCookieStorage(request=self.request, response=base_response)
        storage._do_set(10)
        expected = ['Set-Cookie: geoip_location_id=10', 'expires=Thu, 02-Jan-2031 00:00:00 GMT']
        self.assertEqual(base_response.cookies[settings.GEOIP_COOKIE_NAME].output().split('; ')[:2], expected)

    @patch.object(settings, 'GEOIP_COOKIE_DOMAIN', '.testserver.local')
    def test_get_cookie_domain_from_settings(self):
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage.get_cookie_domain(), '.testserver.local')

    def test_get_cookie_domain_no_settings(self):
        self.request.get_host = Mock(return_value='my.localserver.tld')
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage.get_cookie_domain(), None)


class LocationDummyStorageTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.location = Mock()

    def test_get(self):
        storage = LocationDummyStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage.get(), self.request.location)

    def test_set(self):
        storage = LocationDummyStorage(request=self.request, response=HttpResponse())
        fake_location = Mock()
        storage.set(fake_location)