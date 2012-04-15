How it works
============

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

IP ranges
~~~~~~~~~

   :members: IpRange


