# -*- coding: utf-8 -*-
from appconf import AppConf

class GeoIpConfig(AppConf):
    COOKIE_NAME = 'geoip_location_id'
    LOCATION_MODEL = 'django_geoip.models.City'
    COOKIE_EXPIRES = 9999999999

    class Meta:
        prefix = 'geoip'