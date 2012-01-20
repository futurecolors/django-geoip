# -*- coding: utf-8 -*-
from django import http
from django_geoip.base import LocationStorage

def set_location(request):
    """
    Redirect to a given url while setting the chosen location in the
    cookie. The url and the location_id need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        location_id = request.POST.get('location_id', None)
        if location_id:
            try:
                LocationStorage(request=request, response=response).set(location_id, force=True)
            except ValueError:
                pass
    return response