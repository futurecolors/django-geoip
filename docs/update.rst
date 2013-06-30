.. _update:

Updating GeoIP database
=======================

.. note::
    Currentrly ``django-geoip`` supports only ipgeobase.ru backend.

To update your database with fresh entries
(adds new geography and completely replaces all IpRegions with fresh ones)::

    python manage.py geoip_update


.. warning::
    This is irreversible operation, do not use on production!

    If you wish to clear all geodata prior the sync
    (deletes all Cities, Regions, Countries and IpRanges)::

        python manage.py geoip_update --clear

.. versionadded:: 0.3.1

    To reduce the size of indexes and database you can exclude countries from import.
    It's achieved by specifying only needed county codes in settings::

        IPGEOBASE_ALLOWED_COUNTRIES = ['RU', 'UA']


.. note::
    If you're having ``2006, 'MySQL server has gone away'`` error during database update,
    setting ``max_allowed_packet`` to a higher value might help.
    E.g. ``max_allowed_packet=16M``