# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from django_geoip.management.ipgeobase import IpGeobase


class Command(BaseCommand):
    help = 'Updates django-geoip data stored in db'
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            default=False,
            help=u"Clear tables prior import",
        ),
    )

    def handle(self, *args, **options):
        print u'Updating geoip data...'
        backend = IpGeobase()

        if options.get('clear'):
            backend.clear_database()

        backend.download_files()
        backend.sync_database()