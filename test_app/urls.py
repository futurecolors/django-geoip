# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.template.base import Template
from django.template.response import TemplateResponse

def index_view(request):
    return TemplateResponse(request, Template('test'))

urlpatterns = patterns('',
    ('^$', index_view)
)