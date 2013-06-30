# coding: utf-8
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:
    import StringIO
    StringIO = BytesIO = StringIO.StringIO


def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("NewBase", (base,), {})


try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
next = advance_iterator