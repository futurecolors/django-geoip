# -*- coding: utf-8 -*-
from appconf import AppConf

class GeoIpConfig(AppConf):
    """ GeoIP configuration """

    #: A reference to a :ref:`model <location_model>` that stores custom geography, specific to application.
    LOCATION_MODEL = 'django_geoip.models.GeoLocationFacade'

    #: Persistent storage class for user location
    # (LocationCookieStorage or LocationDummyStorage are available).
    STORAGE_CLASS = 'django_geoip.storage.LocationCookieStorage'

    #: Cookie name for LocationCookieStorage class (stores :ref:`custom location's <location_model>` primary key).
    COOKIE_NAME = 'geoip_location_id'

    #: Cookie domain for LocationCookieStorage class.
    COOKIE_DOMAIN = ''

    #: Cookie lifetime in seconds (1 year by default) for LocationCookieStorage class.
    COOKIE_EXPIRES = 31622400

    class Meta:
        prefix = 'geoip'