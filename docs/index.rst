django-geoip
============

App to figure out where your visitors are from by their IP address.

Detects country, region and city, querying the database with geodata. |br|
Optional :ref:`high-level API <highlevel>` provides user location in request object.

.. note::
    Currentrly ``django-geoip`` supports only `ipgeobase.ru <http://ipgeobase.ru>`_ backend. |br|
    It provides accurate geolocation in Russia and Ukraine only. |br|
    There are plans to add other backends in future releases.

Contents
--------

.. image:: images/geopony.png
   :alt: Django GeoIP Pony
   :align: right

.. toctree::
  :maxdepth: 1

  installation
  usage
  howitworks
  update
  settings
  reference
  djangohosts
  contributing
  changelog
  authors


Contributing
------------

You can grab latest code on ``dev`` branch at Github_.

Feel free to submit issues_, pull requests are also welcome.

Good contributions follow :ref:`simple guidelines <contributing>`

.. _Github: https://github.com/futurecolors/django-geoip
.. _issues: https://github.com/futurecolors/django-geoip/issues

.. |br| raw:: html

   <br />
