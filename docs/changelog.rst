Changelog
=========

0.3.0 (TBA)
-----------
* Added python 3 support (3.2 - 3.3)
* ***IMPORTANT*** Minimum required django 1.4.2, use version 0.2.8, if you don't want to upgrade.
* ``GeoLocationFascade`` alias removed


0.2.8 (2012-12-10)
------------------
* Cookie storage ignores non-integer location_id


0.2.7 (2012-08-28)
------------------
* Fixed country names to be verbal names rather than iso3166 codes
* Minor docs improvements
* Fixed handling of invalid ips passed to geoip


0.2.6 (2012-05-10)
------------------

* Fixed a bug, introduced in 0.2.5, causing old facade name not work as expected.
* ``set_location`` view now accepts both ``location`` and ``location_id``.
* ***BACKWARDS INCOMPATIBLE*** Removed magic ``_get_cookie_domain`` behavior in favor of configuring ``GEOIP_COOKIE_DOMAIN``.


0.2.5 (2012-04-17)
------------------

* ``GeoLocationFascade`` renamed to ``GeoLocationFacade``, old name will work till 0.3


0.2.4 (2012-04-15)
------------------

* Proper datamigration for countrynames
* ``GeoLocationFascade`` defines abstract classmethods
* ``bulk_create`` support for Django 1.4
* Default view url renamed from ``change`` to ``setlocation``
* Improved docs a lot more
* Short tutorial for django-hosts integration


0.2.3 (2012-04-11)
------------------

* Added country names
* Management update command renamed from ``ipgeobase_update`` to ``geoip_update``
* Management command verbose output with progressbar
* Dropped django 1.2 support
* Documentation improved


0.2.2 (2012-01-25)
------------------

* Fixed middleware behavior when ``process_request`` never ran (redirects)
* Improved location storage validation, fixed cookie domain detection
* Added ``Locator.is_store_empty`` function to reveal if geoip detection was made


0.2.1 (2012-01-25)
------------------

* Fixed middleware behavior when request.location is None
* Added ``GEOIP_STORAGE_CLASS`` setting to override default user location storage
* Introduced ``LocationDummyStorage`` class to avoid cookie storage


0.2 (2012-01-20)
----------------

* Major refactoring of the app, added more tests
* Fixed a typo in ``get_availabe_locations``


0.1 (2012-01-18)
----------------

* Initial release