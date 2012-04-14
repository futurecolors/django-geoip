Usage
=====

The app provides both high and low-level APIs to work with geolocation.
Low-level API works super-simple: it discloses geographic location given an IP adress.
High-level API is more complex and deeply integrated in Django: it automatically
detects user location in every request and makes it available as ``request.location``.

.. _lowlevel:

Low-level API usage
-------------------

Low-level API allows you to guess user's location by his IP address.
This function returns a database record, associated with IP's city, region and country.

Here is a basic example::

  from django_geoip.models import IpRange

  ip = "212.49.98.48"

  try:
      geoip_record = IpRange.objects.by_ip(ip)

      print geoip_record.city
      # >> Екатеринбург (Населенный пункт)

      print geoip_record.region
      # >> Свердловская область (Регион)

      print geoip_record.country
      # >> Russia (Страна)

  except IpRange.DoesNotExist:
      print 'Unknown location'

.. _highlevel:

High-level API usage
--------------------

The app provides a convenient way to detect user location automatically.
If you've followed :ref:`advanced installation instructions <advanced>`,
user's location should be accessible via ``request`` object::

    def my_view(request):
        """ Passing location into template """
        ...
        context['location] = request.location
        ...

``request.location`` is an instance of a custom model that you're required to create on your own
(details below).

.. _location_model:

Location model rationale
~~~~~~~~~~~~~~~~~~~~~~~~

Location model suites the basic needs for sites with different content for users,
depending on their location. Ipgeobase forces Country-Region-City geo-hierarchy, but
it's usually too general and not sufficient. Site content might depend on city only,
or vary on custom areas, combining various cities, that don't match actual geographic regions.

In order to abstract geography from business logic, `django-geoip requires a model`,
specific to your own app.

Creating custom location model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a model, that inherits from ``django_geoip.models.GeoLocationFascade``.
It should implement following classmethods:

.. method:: get_available_locations

.. method:: get_by_ip_range(ip_range)
.. method:: get_default_location()


Switching region
----------------

Works very much like `The set_language redirect view`_.
Make sure you've included ``django_geoip.urls`` in your urlpatterns.
Note that ``set_location`` view accepts only POST requests.

.. _The set_language redirect view: https://docs.djangoproject.com/en/1.0/topics/i18n/#the-set-language-redirect-view
