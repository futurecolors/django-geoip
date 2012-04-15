Integrating with django-hosts
=============================

Django-hosts routes requests for specific hosts to different URL schemes defined in modules called “hostconfs”.
Django-geoip plays nice with django-hosts, allowing to redirect user to specific geodomain.

In this example ``www.site.com`` will redirect to ``asia.site.com`` for users from the East
and ``us.site.com`` for american ones. For european users in will remain ``www.site.com``` without redirect
(default location).

0) :ref:`Install and setup django-geoip <basic>`
   Let's assume we have defined this custom location model::

        # app/models.py
        from django_geoip.models import Country, GeoLocationFascade

        class Location(GeoLocationFascade):
            slug = models.SlugField('Site kwarg')
            country = model.ForeignKey(Country)

   This model is referenced in ``settings.py``::

        LOCATION_MODEL = 'app.models.Location'


1) Install and setup django-hosts_

   .. code-block:: bash

       pip install django-hosts==0.4.2

   Make sure you also followed `other steps`_: adding to INSTALLED_APPS, adding a middleware,
   creating ``hosts.py``, setting up ROOT_HOSTCONF and DEFAULT_HOST.

   .. note::

       ``django_geoip.middleware.LocationMiddleware`` should come before ``django_hosts.middleware.HostsMiddleware``
       in ``MIDDLEWARE_CLASSES`` to make things work together.

.. _other steps:
.. _django-hosts: http://readthedocs.org/docs/django-hosts/en/latest/#installation

2) Configure ``host_patterns`` in `hosts.py`::

    host_patterns = patterns('',
        # Default www.sitename.com pattern that redirects users to <location>.sitename.com
        # depending on their IP address
        host(r'www', settings.ROOT_URLCONF, name='www', callback=detect_location),

        # Geodomain for specific region: <location>.sitename.com, doesn't redirect
        host(r'(?P<site_slug>[\w-]+)', settings.ROOT_URLCONF, name='location', callback=save_location),
    )

3) Define ``detect_location`` callback_::

    from django_geoip.base import location_model, Locator
    from django_hosts.reverse import reverse_host

    def detect_location(request):
        """ Callback takes request object and redirects to specific location domain if appropriate """

        default_location = location_model.get_default_location()

        # User is a first-timer and doesn't have a cookie with detected location
        if Locator(request).is_store_empty():
            # If we're at www-address, but not from default location, then do redirect.
            if request.location != default_location:
                return _redirect(request, domain=reverse_host('location', kwargs={'site_slug': request.location.slug}))
        request.location = default_location

.. _callback: http://readthedocs.org/docs/django-hosts/en/latest/callbacks.html

4) Define ``save_location`` callback::

    def save_location(request, site_slug):
        """ Store location in request, overriding geoip detection """
        request.location = get_object_or_404(Location, slug=site_slug)

