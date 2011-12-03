# -*- coding: utf-8 -*-
import tempfile
from zipfile import ZipFile
from django.core.management.base import BaseCommand
from django.conf import settings
import urllib2
from django_geoip.models import City, Region, Country, IpRange

class Command(BaseCommand):
    help = 'Updates ipgeobase'
    incoming = {'countries': set(),
                'city_country_mapping': {}
    }

    def handle(self, *args, **options):
        print u'Updating ipgeobase...'
        files = self._download_extract_archive(settings.IPGEOBASE_SOURCE_URL)
        cidr_info = self._process_cidr_file(files['cidr'])
        city_info = self._process_cities_file(files['cities'], cidr_info['city_country_mapping'])
        self._update_geography(cidr_info['countries'],
                               city_info['regions'],
                               city_info['cities'])
        self._update_cidr()

    def _download_extract_archive(self, url):
        """ Returns dict with 2 extracted filenames """
        try:
            temp_dir = tempfile.mkdtemp()
            archive = ZipFile(urllib2.urlopen(url).read())
            file_cities = archive.extract(settings.IPGEOBASE_CITIES_FILENAME, path=temp_dir)
            file_cidr = archive.extract(settings.IPGEOBASE_CIDR_FILENAME, path=temp_dir)
            return {'cities': file_cities, 'cidr': file_cidr}
        except urllib2.URLError:
            raise

    def _line_to_dict(self, file, field_names):
        """ Converts file line into dictonary """
        for line in file:
            decoded_line = line.decode(settings.IPGEOBASE_FILE_ENCODING)
            delimiter = settings.IPGEOBASE_FILE_FIELDS_DELIMITER
            yield self._extract_data_from_line(decoded_line, field_names, delimiter)

    def _extract_data_from_line(self, line, field_names=None, delimiter="\t"):
        return dict(zip(field_names, line.rstrip('\n').split(delimiter)))

    def _process_cidr_file(self, file):
        """ Iterate over ip info and extract useful data """
        data = {'cidr': list(), 'countries': set(), 'city_country_mapping': dict()}
        for cidr_info in self._line_to_dict(file, field_names=settings.IPGEOBASE_CIDR_FIELDS):
            data['cidr'].append({'start_ip': cidr_info['start_ip'],
                                  'end_ip': cidr_info['end_ip'],
                                  'country_id': cidr_info['country_code'],
                                  'city_id': cidr_info['city_id']})
            data['countries'].add(cidr_info['country_code'])
            if cidr_info['city_id'] != '-':
                data['city_country_mapping'].update({cidr_info['city_id']: cidr_info['country_code']})
        return data

    def _process_cities_file(self, file, city_country_mapping):
        """ Iterate over cities info and extract useful data """
        data = {'regions': list(), 'cities': list(), 'city_region_mapping': dict()}
        for geo_info in self._line_to_dict(file, field_names=settings.IPGEOBASE_CITIES_FIELDS):
            geo_info['country_code'] = city_country_mapping[geo_info['city_id']]
            data['regions'].append({'name': geo_info['region_name'],
                                    'country__code': geo_info['country_code']})
            data['cities'].append({'region__name': geo_info['region_name'],
                                   'name': geo_info['city_name'],
                                   'id': geo_info['city_id']})
        return data

    def _update_geography(self, countries, regions, cities):
        """ Update database with new countries, regions and cities """
        existing = {
            'cities': list(City.objects.values('name', 'region__name', 'id')),
            'regions': list(Region.objects.values('name', 'country')),
            'countries': Country.objects.values_list('code', flat=True)
        }
        for country_code in countries:
            if country_code not in existing['countries']:
                Country.objects.create(code=country_code, name=country_code)
        for entry in regions:
            if entry not in existing['regions']:
                Region.objects.create(name=entry['name'], country_id=entry['country'])
        for entry in cities:
            if entry not in existing['cities']:
                region = Region.objects.get(name=entry['region__name'])
                City.objects.create(id=entry['id'], name=entry['name'], region=region)

    def _update_cidr(self):
        """ Rebuild IPRegion table with fresh data (old ip ranges are removed for simplicity)"""
        city_region_mapping = self._build_city_region_mapping()
        IpRange.objects.all().delete()
        for entry in self.incoming['cidr']:
            entry.update({'city_id': city_region_mapping[entry['city_id']]})
            IpRange.objects.create(**entry)

    def _build_city_region_mapping(self):
        cities = City.objects.values_list('id', 'region__id')
        city_region_mapping = {}
        for city in cities:
            city_region_mapping.update({city[0]: city[1]})
        return city_region_mapping
