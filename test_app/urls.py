# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.http import HttpResponse
from django_geoip.views import set_location

def index_view(request):
    return HttpResponse()

urlpatterns = patterns('',
    ('^$', index_view),
    ('^set_location/$', set_location),
    ('^hello/$', index_view),
)