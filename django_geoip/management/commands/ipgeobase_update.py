# -*- coding: utf-8 -*-
from cStringIO import StringIO
from optparse import make_option
import tempfile
from zipfile import ZipFile
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
import urllib2
from django_geoip.models import City, Region, Country, IpRange

class Command(BaseCommand):
    help = 'Updates ipgeobase'
    incoming = {'countries': set(),
                'city_country_mapping': {}
    }
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            default=False,
            help=u"Clear tables prior import",
        ),
    )

    def handle(self, *args, **options):
        print u'Updating ipgeobase...'
        files = self._download_extract_archive(settings.IPGEOBASE_SOURCE_URL)
        cidr_info = self._process_cidr_file(open(files['cidr'], 'r'))
        city_info = self._process_cities_file(open(files['cities'], 'r'),
                                              cidr_info['city_country_mapping'])
        if options.get("clear_db"):
            IpRange.objects.all().delete()
            City.objects.all().delete()
            Region.objects.all().delete()
            Country.objects.all().delete()
        self._update_geography(cidr_info['countries'],
            city_info['regions'],
            city_info['cities'])
        self._update_cidr(cidr_info)

    def _download_url_to_string(self, url):
        f = urllib2.urlopen(url)
        buffer = StringIO(f.read())
        f.close()
        return buffer

    def _download_extract_archive(self, url):
        """ Returns dict with 2 extracted filenames """
        try:
            temp_dir = tempfile.mkdtemp()
            archive = ZipFile(self._download_url_to_string(url))
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
            city_id = cidr_info['city_id'] if cidr_info['city_id'] != '-' else None
            data['cidr'].append({'start_ip': cidr_info['start_ip'],
                                 'end_ip': cidr_info['end_ip'],
                                 'country_id': cidr_info['country_code'],
                                 'city_id': city_id})
            data['countries'].add(cidr_info['country_code'])
            if city_id is not None:
                data['city_country_mapping'].update({cidr_info['city_id']: cidr_info['country_code']})
        return data

    def _get_country_code_for_city(self, city_id, mapping, added_data):
        """ Get coutry code for city, if we don't know exactly, lets take last used country"""
        try:
            return mapping[city_id]
        except KeyError:
            return added_data[-1]['country__code']

    def _process_cities_file(self, file, city_country_mapping):
        """ Iterate over cities info and extract useful data """
        data = {'regions': list(), 'cities': list(), 'city_region_mapping': dict()}
        for geo_info in self._line_to_dict(file, field_names=settings.IPGEOBASE_CITIES_FIELDS):
            country_code = self._get_country_code_for_city(geo_info['city_id'], city_country_mapping, data['regions'])
            new_region = {'name': geo_info['region_name'],
                          'country__code': country_code}
            if new_region not in data['regions']:
                data['regions'].append(new_region)
            data['cities'].append({'region__name': geo_info['region_name'],
                                   'name': geo_info['city_name'],
                                   'id': geo_info['city_id'],
                                   'latitude': Decimal(geo_info['latitude']),
                                   'longitude': Decimal(geo_info['longitude'])})
        return data

    def _update_geography(self, countries, regions, cities):
        """ Update database with new countries, regions and cities """
        existing = {
            'cities': list(City.objects.values_list('id', flat=True)),
            'regions': list(Region.objects.values('name', 'country__code')),
            'countries': Country.objects.values_list('code', flat=True)
        }
        for country_code in countries:
            if country_code not in existing['countries']:
                Country.objects.create(code=country_code, name=country_code)
        for entry in regions:
            if entry not in existing['regions']:
                Region.objects.create(name=entry['name'], country_id=entry['country__code'])
        for entry in cities:
            if long(entry['id']) not in existing['cities']:
                region = Region.objects.get(name=entry['region__name'])
                City.objects.create(id=entry['id'], name=entry['name'], region=region,
                                    latitude=entry.get('latitude'), longitude=entry.get('longitude'))

    def _update_cidr(self, cidr):
        """ Rebuild IPRegion table with fresh data (old ip ranges are removed for simplicity)"""
        IpRange.objects.all().delete()
        city_region_mapping = self._build_city_region_mapping()
        for entry in cidr['cidr']:
            # skipping for country rows
            if entry['city_id']:
                entry.update({'region_id': city_region_mapping[int(entry['city_id'])]})
            IpRange.objects.create(**entry)

    def _build_city_region_mapping(self):
        cities = City.objects.values('id', 'region__id')
        city_region_mapping = {}
        for city in cities:
            if city['id']:
                city_region_mapping.update({city['id']: city['region__id']})
        return city_region_mapping
