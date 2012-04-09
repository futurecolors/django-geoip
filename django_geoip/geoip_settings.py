# -*- coding: utf-8 -*-
from appconf import AppConf

class GeoIpConfig(AppConf):
    """ GeoIP configuration """

    #: Provide a model that stores geography, specific to your application
    LOCATION_MODEL = 'django_geoip.models.GeoLocationFascade'

    #: Persistant storage class for user location (cookies or dummy are available)
    STORAGE_CLASS = 'django_geoip.storage.LocationCookieStorage'

    #: Cookie stores location model primary key
    COOKIE_NAME = 'geoip_location_id'

    #: Fill in for custom case
    COOKIE_DOMAIN = ''

    #: Cookie lifetime in seconds (1 year by default)
    COOKIE_EXPIRES = 31622400

    class Meta:
        prefix = 'geoip'