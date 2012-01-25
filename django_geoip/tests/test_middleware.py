# -*- coding: utf-8 -*-
from django.conf import settings
from django_geoip import middleware
from django.http import HttpResponse
from django_any.models import any_model
from django_any.test import Client
from mock import patch, Mock
import django_geoip
from django_geoip.base import  Locator
from django_geoip.models import City
from django_geoip.storage import LocationCookieStorage
from django_geoip.tests import unittest
from test_app.models import MyCustomLocation

try:
    from django.test.client import RequestFactory
except ImportError:
    RequestFactory = None

@unittest.skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class MiddlewareTest(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        self.client = Client()
        self.factory = RequestFactory()
        self.request = self.factory.get('/', **{'REMOTE_ADDR': '6.6.6.6'})
        self.middleware = django_geoip.middleware.LocationMiddleware()

        self.get_location_patcher = patch.object(middleware, 'get_location')
        self.get_location_patcher.start()
        self.get_location_mock = self.get_location_patcher.start()

    def tearDown(self):
        self.get_location_patcher.stop()

    def test_get_location_lazy(self):
        self.client.get('/')
        self.assertEqual(self.get_location_mock.call_count, 0)

    def test_process_request(self):
        self.get_location_mock.return_value = None
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.location, None)
        self.assertEqual(self.get_location_mock.call_count, 1)

    @patch('django_geoip.storage.LocationCookieStorage.set')
    @patch.object(LocationCookieStorage, '__init__')
    def test_process_response_ok(self, mock, mock_location_set):
        mock.return_value = None
        base_response = HttpResponse()
        self.get_location_mock.return_value = mycity = any_model(City)
        self.middleware.process_request(self.request)
        self.middleware.process_response(self.request, base_response)
        mock.assert_called_once_with(request=self.request, response=base_response)
        # workaround simplelazyobject
        self.assertEqual(str(mycity), str(mock_location_set.call_args[1]['location']))

    @patch('django_geoip.storage.LocationCookieStorage._do_set')
    def test_process_response_empty_request_location(self, mock_do_set):
        base_response = HttpResponse()
        self.request.location = None
        self.middleware.process_response(self.request, base_response)
        self.assertFalse(mock_do_set.called)

    @patch('django_geoip.storage.LocationCookieStorage.set')
    def test_process_response_no_request_location(self, mock_set):
        base_response = HttpResponse()
        self.middleware.process_response(self.request, base_response)
        self.assertFalse(mock_set.called)


@unittest.skipIf(RequestFactory is None, "RequestFactory is avaliable from 1.3")
class GetLocationTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self.client = Client()
        self.factory = RequestFactory()

        any_model(MyCustomLocation, pk=1, city__name='city1')
        self.my_location = any_model(MyCustomLocation, id=200, city__name='city200')

    def tearDown(self, *args, **kwargs):
        City.objects.all().delete()

    @patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
    def test_get_stored_location_ok(self):
        self.factory.cookies[settings.GEOIP_COOKIE_NAME] = 200
        request = self.factory.get('/')
        self.assertEqual(Locator(request)._get_stored_location(), self.my_location)

    @patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
    def test_get_stored_location_none(self):
        request = self.factory.get('/')
        self.assertEqual(Locator(request)._get_stored_location(), None)