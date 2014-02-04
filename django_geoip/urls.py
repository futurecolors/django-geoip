# -*- coding: utf-8 -*-
try:
    from django.conf.urls import *
except ImportError:
    from django.conf.urls.defaults import *

from django_geoip.views import set_location

urlpatterns = patterns('',
    url(r'^setlocation/', set_location, name='geoip_change_location'),
)
