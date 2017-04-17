# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject


def get_location(request):
    from django_geoip.base import Locator
    if not hasattr(request, '_cached_location'):
        request._cached_location = Locator(request).locate()
    return request._cached_location


class LocationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """ Don't detect location, until we request it implicitly """
        request.location = SimpleLazyObject(lambda: get_location(request))
