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


.. note::
    If you're having ``2006, 'MySQL server has gone away'`` error during database update,
    setting ``max_allowed_packet`` to a higher value might help.
    E.g. ``max_allowed_packet=16M``