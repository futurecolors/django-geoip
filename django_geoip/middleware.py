# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject
from django_geoip.base import storage_class


def get_location(request):
    from django_geoip.base import Locator
    if not hasattr(request, '_cached_location'):
        request._cached_location = Locator(request).locate()
    return request._cached_location


class LocationMiddleware(object):

    def process_request(self, request):
        # Don't detect location, until we request it implicitly
        request.location = SimpleLazyObject(lambda: get_location(request))

    def process_response(self, request, response):
        storage = storage_class(request=request, response=response)
        try:
            storage.set(location=request.location)
        except ValueError:
            # bad location_id
            pass
        return response
