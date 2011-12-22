# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from django.conf import settings
from django.utils.functional import SimpleLazyObject

def get_location(request):
    from django_geoip import get_location_from_request
    if not hasattr(request, '_cached_location'):
        request._cached_location = get_location_from_request(request)
    return request._cached_location

def check_for_location(location_id):
    """ Check that location exists """
    return True

def set_location_cookie(response, value):
    response.set_cookie(settings.GEOIP_COOKIE_NAME, value,
        expires = datetime.now() + timedelta(seconds=settings.GEOIP_COOKIE_EXPIRES))

class LocationMiddleware(object):
    def process_request(self, request):
        request.location = SimpleLazyObject(lambda: get_location(request))

    def _should_update_cookie(self, request):
        # process_request never completed, don't need to update cookie
        if not hasattr(request, 'location'):
            return False
        # Cookie doesn't exist, we need to store it
        if settings.GEOIP_COOKIE_NAME not in request.COOKIES:
            return True
        # Cookie is obsolete, because we've changed it's value during request
        if str(request.COOKIES[settings.GEOIP_COOKIE_NAME]) != str(request.location.id):
            return True
        return False

    def process_response(self, request, response):
        if self._should_update_cookie(request):
            set_location_cookie(response, request.location.id)
        return response
