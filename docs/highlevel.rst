High-level API usage
====================

The app provides a convenient way to detect user location automatically.
If you've followed advanced installation instructions, you can access
user's location in your ``request`` object::

    def my_view(request):
        """ Passing location into template """
        ...
        context['location] = request.location
        ...

User location is an instance of a custom model that you're required to create on your own
(details below).

To avoid unnecessary database hits user location id is stored in a cookie.

Location model
--------------

Location model suites the basic needs for sites with different content for users,
depending on their location. Ipgeobase forces Country-Region-City geo-hierarchy, but
it's usually too general and not sufficient. Site content might depend on city only,
or vary on custom areas, combining various cities, that don't match actual geographic regions.

In order to abstract geography from business logic, django-geoip requires a model,
specific to your own app.

Creating custom location model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a model, that inherits from ``django_geoip.models.GeoLocationFascade``.
It should implement following classmethods:

.. automodule:: django_geoip.models
   :members: GeoLocationFascade


Switching region
----------------

Works very much like `The set_language redirect view`_.
Make sure you've included ``django_geoip.urls`` in your urlpatterns.
Note that ``set_location`` view accepts only POST requests.

.. _The set_language redirect view: https://docs.djangoproject.com/en/1.0/topics/i18n/#the-set-language-redirect-view