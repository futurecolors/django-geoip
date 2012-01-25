# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django_any.models import any_model
from mock import patch, Mock
from django_geoip.storage import LocationCookieStorage, LocationDummyStorage, BaseLocationStorage
from django_geoip.tests import unittest
from test_app.models import MyCustomLocation

class BaseLocationStorageTest(unittest.TestCase):

    def setUp(self):
        self.settings_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
        self.settings_patcher.start()

        self.storage = BaseLocationStorage(request=HttpRequest(), response=HttpResponse())

    def tearDown(self):
        self.settings_patcher.stop()

    def test_validate_location(self):
        self.assertFalse(self.storage._validate_location(None))
        self.assertFalse(self.storage._validate_location(Mock()))

        location = any_model(MyCustomLocation)
        self.assertTrue(self.storage._validate_location(location))


class LocationCookieStorageTest(unittest.TestCase):

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

    @patch('django_geoip.storage.datetime')
    def test_do_set(self, mock):
        mock.now.return_value = datetime(2012, 1, 1, 0, 0, 0)
        base_response = HttpResponse()
        storage = LocationCookieStorage(request=self.request, response=base_response)
        storage._do_set(10)
        expected = 'Set-Cookie: geoip_location_id=10; expires=Tue, 20-Nov-2328 17:46:39 GMT;'
        self.assertTrue(base_response.cookies[settings.GEOIP_COOKIE_NAME].output().startswith(expected))

    @patch.object(settings, 'GEOIP_COOKIE_DOMAIN', '.testserver.local')
    def test_get_cookie_domain_from_settings(self):
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage._get_cookie_domain(), '.testserver.local')

    def test_get_cookie_domain_remove_first_part(self):
        self.request.get_host = Mock(return_value='my.localserver.tld')
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage._get_cookie_domain(), '.localserver.tld')

    def test_get_cookie_domain_cant_find_first_part(self):
        self.request.get_host = Mock(return_value=None)
        storage = LocationCookieStorage(request=self.request, response=HttpResponse())
        self.assertEqual(storage._get_cookie_domain(), None)


class LocationDummyStorageTest(unittest.TestCase):

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

