# coding: utf-8
from django.conf.urls import url, include
from django.http import HttpResponse
from django_geoip.views import set_location


def index_view(request):
    return HttpResponse()


urlpatterns = [
    url('^$', index_view),
    url(r'^geoip/', include('django_geoip.urls')),
    url('^hello/$', index_view),
]
