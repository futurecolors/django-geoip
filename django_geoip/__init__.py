# -*- coding: utf-8 -*-
from django.conf import settings
from django_geoip.models import IpRange

def get_location(request):
    cached_location = _get_cached_location(request)
    if not cached_location:
        entry = _get_geobase_entry(request)
        cached_location = _get_corresponding_location(entry)
    return cached_location

def _get_cached_location(request):
    """ Get location from cookie """
    return None
    model_class = settings.GEOIP_LOCATION_MODEL
    location_id = request.COOKIES.get(settings.GEOIP_COOKIE_NAME, None)
    try:
        model_class.objects.get(pk=location_id)
    except model_class.DoesNotExist:
        return None


def _get_real_ip(request):
    """ Get IP from request """
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        return real_ip.split(",")[0]
    except KeyError:
        return request.META['REMOTE_ADDR']
    except Exception:
        # Unknown IP
        return None

def _get_corresponding_location(ip_range):
    model_class = settings.GEOIP_LOCATION_MODEL
    return ip_range.city

def _get_geobase_entry(request):
    """ Fetches IpRange instance if request IP is found in database """
    ip = _get_real_ip(request)
    try:
        geobase_entry = IpRange.objects.by_ip(ip)
    except IpRange.DoesNotExist:
        geobase_entry = None
    return geobase_entry
