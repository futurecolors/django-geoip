Changelog
=========

0.2.4dev (2012-04-??)
---------------------

* Added proper datamigration for countrynames
* GeoLocationFascade has abstract classmethods
* Added bulk_create support for Django 1.4


0.2.3 (2012-04-11)
------------------

* Added country names
* Management update command renamed from ``ipgeobase_update`` to ``geoip_update``
* Management command verbose output with progressbar
* Dropped django 1.2 support
* Documentation improved


0.2.2 (2012-01-25)
------------------

* Fixed middleware behavior when preocess_request never ran (redirects)
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