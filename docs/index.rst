django-geoip
============

App to figure out where your visitors are from by their IP address.

.. note::
    Currentrly ``django-geoip`` supports only `ipgeobase.ru <http://ipgeobase.ru>`_ backend. |br|
    It provides accurate geolocation in Russia and Ukraine only. |br|
    There are plans to add other backends in future releases.

Contents
--------

.. toctree::
  :maxdepth: 1

  installation
  usage
  howitworks
  backends
  update
  settings
  reference
  djangohosts
  tests
  changelog

Development
-----------

You can grab latest code on dev branch at Github_.

Feel free to submit issues_, pull requests are also welcome.

.. _Github: https://github.com/coagulant/django-geoip
.. _issues: https://github.com/coagulant/django-geoip/issues

Tests
-----

You can run testsuite this way::

    python manage.py runtests.py

.. |br| raw:: html

   <br />
