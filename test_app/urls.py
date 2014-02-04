# coding: utf-8
try:
    from django.conf.urls import patterns, include
except ImportError:
    from django.conf.urls.defaults import patterns, include
from django.http import HttpResponse
from django_geoip.views import set_location


def index_view(request):
    return HttpResponse()


urlpatterns = patterns('',
    ('^$', index_view),
    (r'^geoip/', include('django_geoip.urls')),
    ('^hello/$', index_view),
)
