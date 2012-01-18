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

.. automodule:: django_geoip.models
   :members: Country, Region, City

IP ranges
~~~~~~~~~

.. automodule:: django_geoip.models
   :members: IpRange


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


