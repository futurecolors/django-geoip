# -*- coding: utf-8 -*-
import io
import tempfile
import logging
import zipfile
from decimal import Decimal

import requests
from django.conf import settings

from django_geoip.vendor.progressbar import ProgressBar, Percentage, Bar
from django_geoip import compat
from django_geoip.models import IpRange, City, Region, Country
from .iso3166_1 import ISO_CODES


class IpGeobase(object):
    """Backend to download and update geography and ip addresses mapping.
    """

    def __init__(self, logger=None):
        self.files = {}
        self.logger = logger or logging.getLogger(name='geoip_update')

    def clear_database(self):
        """ Removes all geodata stored in database.
            Useful for development, never use on production.
        """
        self.logger.info('Removing obsolete geoip from database...')
        IpRange.objects.all().delete()
        City.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()

    def download_files(self):
        self.files = self._download_extract_archive(settings.IPGEOBASE_SOURCE_URL)
        return self.files

    def sync_database(self):
        cidr_info = self._process_cidr_file(io.open(self.files['cidr'], encoding=settings.IPGEOBASE_FILE_ENCODING))
        city_info = self._process_cities_file(io.open(self.files['cities'], encoding=settings.IPGEOBASE_FILE_ENCODING),
            cidr_info['city_country_mapping'])
        self.logger.info('Updating locations...')
        self._update_geography(cidr_info['countries'],
                               city_info['regions'],
                               city_info['cities'],
                               cidr_info['city_country_mapping'])
        self.logger.info('Updating CIDR...')
        self._update_cidr(cidr_info)

    def _download_extract_archive(self, url):
        """ Returns dict with 2 extracted filenames """
        self.logger.info('Downloading zipfile from ipgeobase.ru...')
        temp_dir = tempfile.mkdtemp()
        archive = zipfile.ZipFile(self._download_url_to_string(url))
        self.logger.info('Extracting files...')
        file_cities = archive.extract(settings.IPGEOBASE_CITIES_FILENAME, path=temp_dir)
        file_cidr = archive.extract(settings.IPGEOBASE_CIDR_FILENAME, path=temp_dir)
        return {'cities': file_cities, 'cidr': file_cidr}

    def _download_url_to_string(self, url):
        r = requests.get(url)
        return compat.BytesIO(r.content)

    def _line_to_dict(self, file, field_names):
        """ Converts file line into dictonary """
        for line in file:
            delimiter = settings.IPGEOBASE_FILE_FIELDS_DELIMITER
            yield self._extract_data_from_line(line, field_names, delimiter)

    def _extract_data_from_line(self, line, field_names=None, delimiter="\t"):
        return dict(zip(field_names, line.rstrip('\n').split(delimiter)))

    def _process_cidr_file(self, file):
        """ Iterate over ip info and extract useful data """
        data = {'cidr': list(), 'countries': set(), 'city_country_mapping': dict()}
        allowed_countries = settings.IPGEOBASE_ALLOWED_COUNTRIES
        for cidr_info in self._line_to_dict(file, field_names=settings.IPGEOBASE_CIDR_FIELDS):
            city_id = cidr_info['city_id'] if cidr_info['city_id'] != '-' else None
            if city_id is not None:
                data['city_country_mapping'].update({cidr_info['city_id']: cidr_info['country_code']})

            if allowed_countries and cidr_info['country_code'] not in allowed_countries:
                continue
            data['cidr'].append({'start_ip': cidr_info['start_ip'],
                                 'end_ip': cidr_info['end_ip'],
                                 'country_id': cidr_info['country_code'],
                                 'city_id': city_id})
            data['countries'].add(cidr_info['country_code'])
        return data

    def _get_country_code_for_city(self, city_id, mapping, added_data):
        """ Get country code for city, if we don't know exactly, lets take last used country"""
        try:
            return mapping[city_id]
        except KeyError:
            return added_data[-1]['country__code']

    def _process_cities_file(self, file, city_country_mapping):
        """ Iterate over cities info and extract useful data """
        data = {'all_regions': list(), 'regions': list(), 'cities': list(), 'city_region_mapping': dict()}
        allowed_countries = settings.IPGEOBASE_ALLOWED_COUNTRIES
        for geo_info in self._line_to_dict(file, field_names=settings.IPGEOBASE_CITIES_FIELDS):
            country_code = self._get_country_code_for_city(geo_info['city_id'], city_country_mapping, data['all_regions'])
            new_region = {'name': geo_info['region_name'],
                          'country__code': country_code}
            if new_region not in data['all_regions']:
                data['all_regions'].append(new_region)

            if allowed_countries and country_code not in allowed_countries:
                continue

            if new_region not in data['regions']:
                data['regions'].append(new_region)
            data['cities'].append({'region__name': geo_info['region_name'],
                                   'name': geo_info['city_name'],
                                   'id': geo_info['city_id'],
                                   'latitude': Decimal(geo_info['latitude']),
                                   'longitude': Decimal(geo_info['longitude'])})
        return data

    def _update_geography(self, countries, regions, cities, city_country_mapping):
        """ Update database with new countries, regions and cities """
        existing = {
            'cities': list(City.objects.values_list('id', flat=True)),
            'regions': list(Region.objects.values('name', 'country__code')),
            'countries': Country.objects.values_list('code', flat=True)
        }
        for country_code in countries:
            if country_code not in existing['countries']:
                Country.objects.create(code=country_code, name=ISO_CODES.get(country_code, country_code))
        for entry in regions:
            if entry not in existing['regions']:
                Region.objects.create(name=entry['name'], country_id=entry['country__code'])
        for entry in cities:
            if int(entry['id']) not in existing['cities']:
                code = city_country_mapping.get(entry['id'])
                if code:
                    region = Region.objects.get(name=entry['region__name'], country__code=code)
                    City.objects.create(id=entry['id'], name=entry['name'], region=region,
                                    latitude=entry.get('latitude'), longitude=entry.get('longitude'))

    def _update_cidr(self, cidr):
        """ Rebuild IPRegion table with fresh data (old ip ranges are removed for simplicity)"""
        new_ip_ranges = []
        is_bulk_create_supported = hasattr(IpRange.objects, 'bulk_create')
        IpRange.objects.all().delete()
        city_region_mapping = self._build_city_region_mapping()

        if self.logger.getEffectiveLevel() in [logging.INFO, logging.DEBUG]:
            pbar = ProgressBar(widgets=[Percentage(), ' ', Bar()])
        else:
            pbar = iter
        for entry in pbar(cidr['cidr']):
            # skipping for country rows
            if entry['city_id']:
                entry.update({'region_id': city_region_mapping[int(entry['city_id'])]})
            if is_bulk_create_supported:
                new_ip_ranges.append(IpRange(**entry))
            else:
                IpRange.objects.create(**entry)
        if is_bulk_create_supported:
            IpRange.objects.bulk_create(new_ip_ranges)

    def _build_city_region_mapping(self):
        cities = City.objects.values('id', 'region__id')
        city_region_mapping = {}
        for city in cities:
            if city['id']:
                city_region_mapping.update({city['id']: city['region__id']})
        return city_region_mapping
