How it works
============

TBD

Low-level API usage
-------------------

Here is an example of how can you guess user's location::

  from django_geoip.models import IPGeoBase

  ip = "212.49.98.48"

  try:
      ipgeobases = IpRange.objects.by_ip(ip)
      print ipgeobase.city # Населенный пункт (Екатеринбург)
      print ipgeobase.region # Регион (Свердловская область)
      print ipgeobase.country # Страна (Россия)
  except IpRange.DoesNotExist:
      print u'Unknown location'


