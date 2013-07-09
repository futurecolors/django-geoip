.. _contributing:

Contributing
============

Most of the ``django-geoip`` code is covered with tests, so if you wish to contribute
(which is highly appreciated) please add corresponding tests.

.. image:: https://secure.travis-ci.org/futurecolors/django-geoip.png?branch=dev
    :target: https://travis-ci.org/futurecolors/django-geoip

.. image:: https://coveralls.io/repos/futurecolors/django-geoip/badge.png?branch=dev
    :target: https://coveralls.io/r/futurecolors/django-geoip/

Running tests::

    make test

This command runs only unittests, which is preferred behavior.
However, you might need to run system tests too (might take some time and requires internet connection)::

    make test_system

Checking coverage (requires ``coverage`` package)::

    make coverage

Finally, if you want to run tests against all python-django combinations supported::

    tox

