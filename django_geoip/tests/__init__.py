import sys

try:
    from django.test.client import RequestFactory as my_RequestFactory
except ImportError:
    my_RequestFactory = None
RequestFactory = my_RequestFactory

try:
    import unittest2 as my_unittest
except ImportError:
    if sys.version_info >= (2,7):
        # unittest2 features are native in Python 2.7
        import unittest as my_unittest
    else:
        raise
unittest = my_unittest

from test_management import *
from test_base import *
from test_storage import *
from test_models import *
from test_utils import *
from test_middleware import *
from test_views import *