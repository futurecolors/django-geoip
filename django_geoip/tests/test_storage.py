# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from mock import patch, Mock
from django_geoip.storage import LocationCookieStorage, LocationDummyStorage
from django_geoip.tests import unittest


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

