# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.testcases import TestCase
from django_any.models import any_model
from django_any.test import Client
from test_app.models import MyCustomLocation
from mock import patch

class SetLocationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = '/set_location/'
        self.location = any_model(MyCustomLocation)

        self.location_model_patcher = patch.object(settings, 'GEOIP_LOCATION_MODEL', 'test_app.models.MyCustomLocation')
        self.location_model = self.location_model_patcher.start()

    def tearDown(self):
        self.location_model_patcher.stop()

    def test_get(self):
        response = self.client.get(self.url, data={'location_id': self.location.id})
        self.assertFalse(settings.GEOIP_COOKIE_NAME in response.cookies)
        self.assertRedirects(response, 'http://testserver/')

    def test_get_or_post_next_url(self):
        for method in ['get', 'post']:
            method_call = getattr(self.client, method)
            response = method_call(self.url, data={'next': '/hello/',
                                                   'location_id': self.location.id})
            self.assertRedirects(response, 'http://testserver/hello/')

    def test_post_ok(self):
        response = self.client.post(self.url, data={'location_id': self.location.id})
        self.assertEqual(response.cookies[settings.GEOIP_COOKIE_NAME].value, str(self.location.id))
        self.assertRedirects(response, 'http://testserver/')

    def test_post_fake_location(self):
        response = self.client.post(self.url, data={'location_id': self.location.id+1})
        self.assertFalse(settings.GEOIP_COOKIE_NAME in response.cookies)
        self.assertRedirects(response, 'http://testserver/')