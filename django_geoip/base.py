# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import SimpleLazyObject
from django_geoip.models import IpRange
from django_geoip.utils import get_class


location_model = SimpleLazyObject(
    lambda: get_class(settings.GEOIP_LOCATION_MODEL))

storage_class = get_class(settings.GEOIP_STORAGE_CLASS)


class Locator(object):
    """ A helper class that automates user location detection
    """

    def __init__(self, request):
        self.request = request

    def locate(self):
        """ Find out what is user location (either from his ip or cookie)

        :return: Custom location model
        """
        stored_location = self._get_stored_location()
        if not stored_location:
            ip_range = self._get_ip_range()
            stored_location = self._get_corresponding_location(ip_range)
        return stored_location

    def _get_corresponding_location(self, ip_range):
        """
        Get user location by IP range, if no location matches, returns default location.

        :param ip_range: An instance of IpRange model
        :type ip_range: IpRange
        :return: Custom location model
        """
        try:
            return location_model.get_by_ip_range(ip_range)
        except ObjectDoesNotExist:
            return location_model.get_default_location()

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

    def _get_stored_location(self):
        """ Get location from cookie

        :param request: A ususal request object
        :type request: HttpRequest
        :return: Custom location model
        """
        location_storage = storage_class(request=self.request, response=None)
        return location_storage.get()

