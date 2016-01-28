# -*- coding: utf-8 -*-
try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

from django_geoip.views import set_location

urlpatterns = [
    url(r'^setlocation/', set_location, name='geoip_change_location'),
]
