django-geoip
============

App to figure out where your visitors are from by their IP address.

Right now django-geoip is based on ipgeobase.ru data and provides accurate
geolocation in Russia and Ukraine only. There are plans to add other backends
in future releases.

Contents
--------

.. toctree::
  :maxdepth: 2

  installation
  howitworks
  highlevel
  update
  reference
  changelog

Development
-----------

You can grab latest code on dev branch at `Github <https://github.com/coagulant/django-geoip>`_.

Feel free to submit `issues <https://github.com/coagulant/django-geoip/issues>`_, pull requests are also welcome.

Tests
-----

You can run testsuite this way::

    python manage.py runtests.py
