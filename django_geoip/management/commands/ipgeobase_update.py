# -*- coding: utf-8 -*-
from zipfile import ZipFile
from django.core.management.base import BaseCommand
import urllib2
from django_geoip.models import City, Region, Country, IpRange

class Command(BaseCommand):
    help = 'Updates ipgeobase'
    incoming = {}

    SOURCE_URL = 'http://ipgeobase.ru/files/db/Main/geo_files.zip'
    FIELDS_DELIMITER = "\t"
    ENCODING = 'windows-1251'

    CITIES_FILENAME = 'cities.txt'
    #    1	Хмельницкий	Хмельницкая область	Центральная Украина	49.416668	27.000000
    CITIES_FIELDS = ['city_id', 'city_name', 'region_name', 'district_name', 'lat', 'lng']

    CIDR_FILENAME = 'cidr_optim.txt'
    #    1578795008	1578827775	94.26.128.0 - 94.26.255.255	RU	2287
    CIDR_FIELDS = ['start_ip', 'end_ip', 'ip_range_human', 'country_code', 'city_id']


    def handle(self, *args, **options):
        print u'Updating ipgeobase...'
        archive = self._download_unpack_archive()
        self._process_cidr_file(archive)
        self._process_cities_file(archive)
        self._update_geography()
        self._update_cidr()

    def _download_unpack_archive(self):
        """ Returns ZipFile instance """
        try:
            archive = urllib2.urlopen(self.SOURCE_URL).read()
            return ZipFile(archive)
        except urllib2.URLError:
            raise

    def _process_cidr_file(self, archive):
        """ Iterate over ip info and extract useful data """
        self.incoming['countries'] = set()
        self.incoming['city_country_mapping'] = {}
        for line in archive.open(self.CIDR_FILENAME):
            cidr_info = dict(zip(self.CIDR_FIELDS, line.decode(self.ENCODING).split(self.FIELDS_DELIMITER)))
            self.incoming['cidr'].update({'start_ip': cidr_info['start_ip'],
                                          'end_ip': cidr_info['end_ip'],
                                          'country_id': cidr_info['country_code'],
                                          'city_id': cidr_info['city_id']})
            self.incoming['countries'].update({'code': cidr_info['country_code']})
            self.incoming['city_country_mapping'].update({cidr_info['city_id']: cidr_info['country_code']})

    def _process_cities_file(self, archive):
        """ Iterate over cities info and extract useful data """
        self.incoming['regions'] = set()
        self.incoming['cities'] = set()
        self.incoming['city_region_mapping'] = {}
        for line in archive.open(self.CITIES_FILENAME):
            geo_info = dict(zip(self.CITIES_FIELDS, line.decode(self.ENCODING).split(self.FIELDS_DELIMITER)))
            geo_info['country_code'] = self.incoming['city_country_mapping'][geo_info['city_id']]
            self.incoming['cities'].update({'region__name': geo_info['region_name'],
                                            'name': geo_info['city_name'],
                                            'id': geo_info['city_id']})
            self.incoming['regions'].update({'name': geo_info['region_name'],
                                             'country__code': geo_info['country_code']})

    def _update_geography(self):
        """ Update database with new countries, regions and cities """
        existing = {
            'cities': City.objects.values_list('name', 'region__name', 'id'),
            'regions': Region.objects.values_list('name', 'country__code'),
            'countries': Country.objects.values_list('code')
        }
        for entry in self.incoming['countries']:
            if entry not in existing['countries']:
                country = Country.objects.create(**entry)
        for entry in self.incoming['regions']:
            if entry not in existing['regions']:
                region = Region.objects.create(**entry)
        for entry in self.incoming['cities']:
            if entry not in existing['cities']:
                city = City.objects.create(**entry)

    def _build_city_region_mapping(self):
        cities = City.objects.values_list('id', 'region__id')
        city_region_mapping = {}
        for city in cities:
            city_region_mapping.update({city[0]: city[1]})
        return city_region_mapping

    def _update_cidr(self):
        """ Rebuild IPRegion table with fresh data (old ip ranges are removed for simplicity)"""
        city_region_mapping = self._build_city_region_mapping()
        IpRange.objects.all().delete()
        for entry in self.incoming['cidr']:
            entry.update({'city_id': self.city_region_mapping[entry['city_id']]})
            IpRange.objects.create(**entry)


