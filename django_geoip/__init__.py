# -*- coding: utf-8 -*-
from django.conf import settings
from django_geoip.models import IpRange
from django_geoip.utils import get_class

def get_location_from_request(request):
    """ Find out what is user location (either from his ip or cookie)
    """
    cached_location = _get_cached_location(request)
    if not cached_location:
        entry = _get_geobase_entry(request)
        cached_location = _get_corresponding_location(entry)
    return cached_location

def _get_cached_location(request):
    """ Get location from cookie """
    model_class = get_class(settings.GEOIP_LOCATION_MODEL)
    location_id = request.COOKIES.get(settings.GEOIP_COOKIE_NAME, None)
    try:
        return model_class.objects.get(pk=location_id)
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
    model_class = get_class(settings.GEOIP_LOCATION_MODEL)
    try:
        model_class.get_by_ip_range(ip_range)
    except Exception:
        pass
    default = model_class.get_default_location()
    if default:
        return default
    else:
        return ip_range.city

def _get_geobase_entry(request):
    """ Fetches IpRange instance if request IP is found in database """
    ip = _get_real_ip(request)
    try:
        geobase_entry = IpRange.objects.by_ip(ip)
    except IpRange.DoesNotExist:
        geobase_entry = None
    return geobase_entry