# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.template.base import Template
from django.template.response import TemplateResponse
from django_geoip.views import set_location

def index_view(request):
    return TemplateResponse(request, Template('test'))

urlpatterns = patterns('',
    ('^$', index_view),
    ('^set_location/$', set_location),
    ('^hello/$', index_view),
)