# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from exceptions import ValueError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_geoip.utils import get_class


class BaseLocationStorage(object):
    """ Base class for user location storage
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.location_model = get_class(settings.GEOIP_LOCATION_MODEL)

    def get(self):
        raise NotImplemented

    def set(self, location=None, force=False):
        raise NotImplemented

    def _validate_location(self, location):
        if not isinstance(location, self.location_model):
            return False
        try:
            return self.location_model.objects.filter(pk=location.id).exists()
        except AttributeError:
            raise
            return False


    def _get_by_id(self, location_id):
        return get_class(settings.GEOIP_LOCATION_MODEL).objects.get(pk=location_id)


class LocationDummyStorage(BaseLocationStorage):
    """ Fake storage for debug or when location doesn't neet to be stored
    """
    def get(self):
        return getattr(self.request, 'location', None)

    def set(self, location=None, force=False):
        pass


class LocationCookieStorage(BaseLocationStorage):
    """ Class that deals with saving user location on client's side (cookies)
    """

    def _get_location_id(self):
        return self.request.COOKIES.get(settings.GEOIP_COOKIE_NAME, None)

    def get(self):
        location_id = self._get_location_id()

        if location_id:
            try:
                return self._get_by_id(location_id)
            except ObjectDoesNotExist:
                pass
        return None

    def set(self, location=None, force=False):
        if not self._validate_location(location):
            raise ValueError
        if force or self._should_update_cookie(location.id):
            self._do_set(location.id)

    def _get_cookie_domain(self):
        """
            TODO: More clever domain detection for common cookies
        """
        if settings.GEOIP_COOKIE_DOMAIN:
            return settings.GEOIP_COOKIE_DOMAIN
        try:
            current_host = self.request.get_host()
            return current_host[current_host.index('.'):]
        except Exception:
            return None

    def _do_set(self, value):
        self.response.set_cookie(
            key=settings.GEOIP_COOKIE_NAME,
            value=value,
            domain=self._get_cookie_domain(),
            expires=datetime.now() + timedelta(seconds=settings.GEOIP_COOKIE_EXPIRES))

    def _should_update_cookie(self, new_value):
        # process_request never completed, don't need to update cookie
        if not hasattr(self.request, 'location'):
            return False
        # Cookie doesn't exist, we need to store it
        if settings.GEOIP_COOKIE_NAME not in self.request.COOKIES:
            return True
        # Cookie is obsolete, because we've changed it's value during request
        if str(self._get_location_id()) != str(new_value):
            return True
        return False