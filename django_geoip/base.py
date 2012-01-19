# -*- coding: utf-8 -*-
from django.conf import settings
from django_geoip.utils import get_class

class Locator(object):

    def __init__(self):
        self.location_model = get_class(settings.GEOIP_LOCATION_MODEL)

