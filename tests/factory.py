import random
import string
from django_geoip.models import Region, City, Country, IpRange


def _random_str():
    return ''.join(random.choice(string.ascii_letters) for x in range(10))


def any_country(**kwargs):
    name = kwargs.get('name', _random_str())
    code = kwargs.get('code', _random_str())
    return Country.objects.create(name=name, code=code)


def any_region(**kwargs):
    country = kwargs.get('country', any_country())
    return Region.objects.create(name=_random_str(), country=country)


def any_city(**kwargs):
    region = kwargs.get('region', any_region())
    name = kwargs.get('name', _random_str())
    return City.objects.create(name=name, region=region)


def create_custom_location(cls, city__name=None, **kwargs):
    city = any_city(name=city__name) if city__name else any_city()
    return cls.objects.create(city=city, **kwargs)


def create_ip_range(**kwargs):
    creation_kwargs = {'start_ip': 1, 'end_ip': 2}
    creation_kwargs.update(kwargs)
    if not 'country' in creation_kwargs:
        creation_kwargs['country'] = any_country()
    return IpRange.objects.create(**creation_kwargs)