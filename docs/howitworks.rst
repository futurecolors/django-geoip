Under the hood
==============

Data storage
------------

All geoip data, including geograpy and geoip mapping is stored in the database.
To avoid unnecessary database hits user location id is stored in a cookie.

Geography
~~~~~~~~~

Right now django-geoip supports only ipgeobase geography, which consist of following
entities: Country, Region, City. Database maintains normalized relationships between
all entities, i.e. Country has many Regions, Region has many Cities.

.. automodule:: django_geoip.models
   :members: Country, Region, City

.. _iprange:

IP ranges
~~~~~~~~~

.. automodule:: django_geoip.models
   :members: IpRange


Backends
--------

There is currently no infrastructure to use alternative geoip backends,
but it's planned for future releases.

Ipgeobase backend
~~~~~~~~~~~~~~~~~

`ipgeobase.ru <http://ipgeobase.ru>`_ is a database of russian
and ukranian IP networks mapped to geographical locations.

It's maintained by `RuCenter <http://nic.ru>`_ and updated daily.

As of 9 April 2012 it contains info on 952 cities and 145736 Ip Ranges
(some networks doesn't belong to CIS).

Here a is demo of ip detection: http://ipgeobase.ru/
