Installation
============

This app works with python 2.6-2.7, Django 1.2 and higher.

Recommended way to install is pip::

  pip install django-geoip


Basic
-----

* Add ``django_geoip`` to ``INSTALLED_APPS`` in settings.py::

    INSTALLED_APPS = (...
                      'django_geoip',
                      ...
                     )

* Run ``python manage.py syncdb`` or ``python manage.py migrate`` (if you're using South)

* Run ``python manage.py ipgeobase_update`` to obtain latest IpGeoBase data.


Advanced
--------

In order to make user's location detection automatic several other steps are required:

* Add ``LocationMiddleware`` to ``MIDDLEWARE_CLASSES``::

    MIDDLEWARE_CLASSES = (...
        'django_geoip.middleware.LocationMiddleware',
    )

* Include app urls into your urlconf if you want to allow visitors to change their region::

    urlpatterns += patterns('',
        ...
        (r'^geoip/', include('django_geoip.urls')),
    )

* Provide a custom location model (inherited from django_geoip.models.GeoLocationFascade)

* Specify this model in settings::

    GEOIP_LOCATION_MODEL = 'example.models.Location' #example
