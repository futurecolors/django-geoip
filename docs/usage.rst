Usage
=====

The app provides both high and low-level APIs to work with geolocation.
Low-level API works super-simple: it guesses geographic location by an IP adress.
High-level API is more complex and deeply integrated in Django: it automatically
detects user location in every request and makes it available as ``request.location``.

.. _lowlevel:

Low-level API usage
-------------------

Low-level API allows you to guess user's location by his IP address.
This function returns a :ref:`database record <iprange>`, associated with IP's city, region and country.

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

.. _location_model_rationale:

Location model rationale
~~~~~~~~~~~~~~~~~~~~~~~~

Location model suites the basic needs for sites with different content for users,
depending on their location. Ipgeobase forces Country-Region-City geo-hierarchy, but
it's usually too general and not sufficient. Site content might depend on city only,
or vary on custom areas, combining various cities, that don't match actual geographic regions.

In order to abstract geography from business logic, `django-geoip requires a model`,
specific to your own app.


.. _location_model:

Creating custom location model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a django model, that inherits from ``django_geoip.models.GeoLocationFacade``.
It might be a `proxy model`_ that doesn't require a separate database table, but it
might be handy in many cases.

Location should implement following classmethods:

.. method:: get_available_locations

    Returns a queryset of all active custom locations.

.. method:: get_by_ip_range(ip_range)

    Returns single instance of location model, corresponding to specified ip_range.
    Raises ``DoesNotExist`` if no location is associated with give IP address.

.. method:: get_default_location()

    Returns single instance of location model, acting as a fallback when ``get_by_ip_range`` fails.

.. _proxy model: https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-models


.. _location_model_example:

Example of custom location model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Very basic implementation of ``GeoLocationFacade`` for demonstration purpose::

    class MyCustomLocation(GeoLocationFacade):
        """ Location is almost equivalent of geographic City.
            Major difference is that only locations
            from this model are returned by high-level API, so you can
            narrow down the list of cities you wish to display on your site.
        """
        name = models.CharField(max_length=100)
        city = models.OneToOneField(City, related_name='my_custom_location')
        is_default = models.BooleanField(default=False)

        @classmethod
        def get_by_ip_range(cls, ip_range):
            """ IpRange has one to many relationship with Country, Region and City.
                Here we exploit the later relationship."""
            return ip_range.city.my_custom_location

        @classmethod
        def get_default_location(cls):
            return cls.objects.get(is_default=True)

        @classmethod
        def get_available_locations(cls):
            return cls.objects.all()


.. _setlocation:

Switching user's location
-------------------------

Switching location from front-end is very much like `changing language in Django`_
(in fact the code is almost the same with a little bit of difference, docs are a nice rip-off).

    As a convenience, the app comes with a view, ``django_geoip.views.set_location``,
    that sets a user's location and redirects back to the previous page.

    Activate this view by adding the following line to your URLconf:

    .. code-block:: django

        # Note that this example makes the view available at /geoip/change/
        (r'^geoip/', include('django_geoip.urls')),

    The view expects to be called via the POST method, with a location identifier
    ``location_id`` set in request. It saves the location choice in a cookie that is
    by default named ``geoip_location_id``.
    (The name can be changed through the ``GEOIP_COOKIE_NAME`` setting.)

    After setting the language choice, Django redirects the user, following this algorithm:

    * Django looks for a ``next`` parameter in the POST data.
    * If that doesn't exist, or is empty, Django tries the URL in the ``Referrer`` header.
    * If that's empty -- say, if a user's browser suppresses that header -- then the user will be redirected to / (the site root) as a fallback.

    Here's example part of a view rendering a form to change location:

    .. code-block:: django

        def get_context(self, **kwargs):
            return {'LOCATIONS': location_model.get_available_locations()}

    Here's example HTML template code:

    .. code-block:: django

        {% load url from future %}

        <form action="{% url 'geoip_change_location' %}" method="post">
        <input name="next" type="hidden" value="/next/page/" />
            <select name="location_id">
            {% for location in LOCATIONS %}
            <option value="{{ location.id }}">{{ location.name }}</option>
            {% endfor %}
        </select>
        <input type="submit" value="Change" />
        </form>

.. _changing language in Django: https://docs.djangoproject.com/en/1.0/topics/i18n/#the-set-language-redirect-view
