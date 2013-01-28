# -*- coding: utf-8 -*-
import logging
from optparse import make_option

from django.core.management.base import BaseCommand
from ..ipgeobase import IpGeobase


class Command(BaseCommand):

    help = 'Updates django-geoip data stored in db'
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            default=False,
            help="Clear tables prior import"
        ),
    )

    def get_logger(self, verbosity):
        logger = logging.getLogger('import')
        logger.addHandler(logging.StreamHandler())
        VERBOSITY_MAPPING = {
            0: logging.CRITICAL, # no
            1: logging.INFO, # means normal output (default)
            2: logging.DEBUG, # means verbose output
            3: logging.DEBUG, # means very verbose output
        }
        logger.setLevel(VERBOSITY_MAPPING[int(verbosity)])
        return logger

    def handle(self, *args, **options):
        logger = self.get_logger(options['verbosity'])
        backend = IpGeobase(logger=logger)

        if options.get('clear'):
            backend.clear_database()

        backend.download_files()
        backend.sync_database()