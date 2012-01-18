How it works
============

Data storage
------------

All geoip data, including geograpy and geoip mapping is stored in the database.

Geography
~~~~~~~~~

Right now django-geoip supports only ipgeobase geography, which consist of following
entities: Country, Region, City. Database maintains normalized relationships between
all entities, i.e. Country has many Regions, Region has many Cities.

IP ranges
~~~~~~~~~

IP ranges are stored in separate table, one row for each ip range.
Each range might be associated with either country (for IP ranges outside of Russia and Ukraine)
or country, region and city together.


High-level API usage
--------------------

The app provides a convenient way to detect user location automatically.
If you've followed advanced installation instructions, you can access
user's location in your ``request`` object.

Location model
~~~~~~~~~~~~~~

Location model suites the basic needs for sites with different content for users,
depending on their location. Ipgeobase forces Country-Region-City location hierarchy, but
it's usually too general and not sufficient. Site content might depend on city only,
or vary on custom Regions, that don't match actual geographic regions.

In order to abstract geography from business logic, django-geoip requires a Location model,
specific to your own app.

Techincal details
~~~~~~~~~~~~~~~~~~

Create a model, that inherits from ``django_geoip.models.GeoLocationFascade``.
It should implement following classmethods:

TBD

Switching region
~~~~~~~~~~~~~~~~
TBD


Low-level API usage
-------------------

Here is an example of how can you guess user's location::

  from django_geoip.models import IpRange

  ip = "212.49.98.48"

  try:
      ipgeobases = IpRange.objects.by_ip(ip)
      print ipgeobase.city # Населенный пункт (Екатеринбург)
      print ipgeobase.region # Регион (Свердловская область)
      print ipgeobase.country # Страна (Россия)
  except IpRange.DoesNotExist:
      print u'Unknown location'


