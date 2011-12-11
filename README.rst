Django GeoIP
============

App to figure out where your visitors are from by their IP address.

Installation
------------

This app works with python 2.5-2.7, Django 1.2 and higher.

Recommended way to install is pip::

  pip install django-geoip


* Add ``django_geoip`` to ``INSTALLED_APPS`` in settings.py::

    INSTALLED_APPS = (...
                      'django_geoip',
                      ...
                     )

* Run ``python manage.py syncdb`` or ``python manage.py migrate`` (if you're using South)


Usage
-----

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


GeoIP database update
---------------------

In order to update ipgeobase::

    python manage.py ipgeobase_update


Tests
-----

You can run testsuite this way::

    python manage.py runtests.py

