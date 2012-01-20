# -*- coding: utf-8 -*-
from mock import patch
from django_geoip.tests import unittest
from django_geoip.utils import get_mod_func, get_class

class UtilsTest(unittest.TestCase):
    def test_get_mod_func(self):
        test_hash = {
            'django.views.news.stories.story_detail': ('django.views.news.stories', 'story_detail'),
            'django': ('django', ''),
        }

        for klass, expected_result in test_hash.items():
            self.assertEqual(get_mod_func(klass), expected_result)

    @patch('django.contrib.sessions.backends.base.SessionBase')
    def test_get_class(self, SessionBase):
        """ FIXME: change to fake class"""
        test_hash = {
            'django.contrib.sessions.backends.base.SessionBase': SessionBase,
        }

        for class_string, expected_class_instance in test_hash.items():
            self.assertEqual(get_class(class_string), expected_class_instance)

        self.assertRaises(ImportError, get_class, 'django_geoip.fake')