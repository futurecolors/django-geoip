Running tests
=============

This app uses `nose test framework`_ and django_nose_.

.. _nose test framework: http://readthedocs.org/docs/nose/en/latest/
.. _django_nose: https://github.com/jbalogh/django-nose

Most of the ``django-geoip`` code is covered with tests, so if you wish to contribute
(which is highly appreciated) pelase add corresponging tests.

Running tests::

    python runtests.py

This command rund only unittests, which is preferred behavir.
However, you might need to run system tests too (might take some time and requires internet connection)::

    python runtests -c system.cfg

