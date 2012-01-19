# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django_geoip.base import LocationStorage

def get_location(request):
    from django_geoip.base import Locator
    if not hasattr(request, '_cached_location'):
        request._cached_location = Locator(request).locate()
    return request._cached_location

def check_for_location(location_id):
    """ Check that location exists """
    return True

def set_location_cookie(response, value):
    response.set_cookie(settings.GEOIP_COOKIE_NAME, value,
        expires = datetime.now() + timedelta(seconds=settings.GEOIP_COOKIE_EXPIRES))

class LocationMiddleware(object):
    def process_request(self, request):
        # Don't detect location, until we request it implicitly
        request.location = SimpleLazyObject(lambda: get_location(request))

    def process_response(self, request, response):
        storage = LocationStorage(request=request, response=response)
        storage.set(value=request.location.id)
        return response
