# -*- coding: utf-8 -*-
from appconf import AppConf

class IpGeoBaseConfig(AppConf):
    # URL, where to download ipgeobase file from
    SOURCE_URL = 'http://ipgeobase.ru/files/db/Main/geo_files.zip'

    FILE_FIELDS_DELIMITER = "\t"
    FILE_ENCODING = 'windows-1251'

    CITIES_FILENAME = 'cities.txt'
    #    1	Хмельницкий	Хмельницкая область	Центральная Украина	49.416668	27.000000
    CITIES_FIELDS = ['city_id', 'city_name', 'region_name', 'district_name', 'longitude', 'latitude']

    CIDR_FILENAME = 'cidr_optim.txt'
    #    1578795008	1578827775	94.26.128.0 - 94.26.255.255	RU	2287
    CIDR_FIELDS = ['start_ip', 'end_ip', 'ip_range_human', 'country_code', 'city_id']

    class Meta:
        prefix = 'ipgeobase'