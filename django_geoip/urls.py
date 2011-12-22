# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django_geoip.views import set_location

urlpatterns = patterns('',
    url(r'^change/', set_location, name='geoip_change_location'),
)