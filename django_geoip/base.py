# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_geoip.models import IpRange
from django_geoip.utils import get_class


class LocationStorage(object):
    """ Class that deals with saving user location on client's side (cookies)
    """
    value = None

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.value = self.get()

    def get(self):
        return self.request.COOKIES.get(settings.GEOIP_COOKIE_NAME, None)

    def set(self, value, force=False):
        if not self._validate_location(value):
            raise ValueError
        self.value = value
        if force or self._should_update_cookie():
            self._do_set(value)

    def _do_set(self, value):
        self.response.set_cookie(
            key=settings.GEOIP_COOKIE_NAME,
            value=value,
            expires=datetime.now() + timedelta(seconds=settings.GEOIP_COOKIE_EXPIRES))

    def _validate_location(self, location_id):
        return get_class(settings.GEOIP_LOCATION_MODEL).objects.filter(pk=location_id).exists()

    def _should_update_cookie(self):
        # process_request never completed, don't need to update cookie
        if not hasattr(self.request, 'location'):
            return False
        # Cookie doesn't exist, we need to store it
        if settings.GEOIP_COOKIE_NAME not in self.request.COOKIES:
            return True
        # Cookie is obsolete, because we've changed it's value during request
        if str(self.get()) != str(self.value):
            return True
        return False


class Locator(object):
    """ A helper class that automates user location detection
    """

    def __init__(self, request):
        self.location_model = get_class(settings.GEOIP_LOCATION_MODEL)
        self.request = request

    def locate(self):
        """ Find out what is user location (either from his ip or cookie)

        :return: Custom location model
        """
        cached_location = self._get_cached_location()
        if not cached_location:
            ip_range = self._get_ip_range()
            cached_location = self._get_corresponding_location(ip_range)
        return cached_location

    def _get_corresponding_location(self, ip_range):
        """
        Get user location by IP range, if no location matches, returns default location.

        :param ip_range: An instance of IpRange model
        :type ip_range: IpRange
        :return: Custom location model
        """
        try:
            return self.location_model.get_by_ip_range(ip_range)
        except ObjectDoesNotExist:
            return self.location_model.get_default_location()

    def _get_real_ip(self):
        """
        Get IP from request

        :param request: A usual request object
        :type request: HttpRequest
        :return: ipv4 string or None
        """
        try:
            # Trying to work with most common proxy headers
            real_ip = self.request.META['HTTP_X_FORWARDED_FOR']
            return real_ip.split(',')[0]
        except KeyError:
            return self.request.META['REMOTE_ADDR']
        except Exception:
            # Unknown IP
            return None

    def _get_ip_range(self):
        """
        Fetches IpRange instance if request IP is found in database

        :param request: A ususal request object
        :type request: HttpRequest
        :return: IpRange object or None
        """
        ip = self._get_real_ip()
        try:
            geobase_entry = IpRange.objects.by_ip(ip)
        except IpRange.DoesNotExist:
            geobase_entry = None
        return geobase_entry

    def _get_cached_location(self):
        """ Get location from cookie

        :param request: A ususal request object
        :type request: HttpRequest
        :return: Custom location model
        """
        location_storage = LocationStorage(request=self.request, response=None)
        location_id = location_storage.get()

        if location_id:
            try:
                return self.location_model.objects.get(pk=location_id)
            except ObjectDoesNotExist:
                pass
        return None

