from django.test import TestCase


class IpGeoBaseSystemTest(TestCase):

    def test_whole_management_command(self):
        from django.core import management
        management.call_command('geoip_update', verbosity=0, interactive=False)