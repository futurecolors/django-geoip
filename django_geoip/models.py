# -*- coding: utf-8 -*-
import socket
import struct
from abc import ABCMeta
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _

# keep imports
import warnings
from django_geoip import ipgeobase_settings, geoip_settings


class Country(models.Model):
    """ One country per row, contains country code and country name.
    """
    code = models.CharField(_('country code'), max_length=2, primary_key=True)
    name = models.CharField(_('country name'), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class Region(models.Model):
    """ Region is a some geographical entity that belongs to one Country,
        Cities belong to one specific Region.
        Identified by country and name.
    """
    country = models.ForeignKey(Country, related_name='regions')
    name = models.CharField(_('region name'), max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        unique_together = (('country', 'name'), )


class City(models.Model):
    """ Geopoint that belongs to the Region and Country.
        Identified by name and region.
        Contains additional latitude/longitude info.
    """
    region = models.ForeignKey(Region, related_name='cities')
    name = models.CharField(_('city name'), max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = (('region', 'name'), )


def inet_aton(ip):
    """ Convert string IP representation to integer
    """
    return struct.unpack('!L', socket.inet_aton(ip))[0]


class IpRangeManager(models.Manager):

    def by_ip(self, ip):
        """ Find the smallest range containing the given IP.
        """
        number = inet_aton(ip)
        try:
            return super(IpRangeManager, self).get_query_set()\
                                              .filter(start_ip__lte=number, end_ip__gte=number)\
                                              .order_by('end_ip', '-start_ip')[0]
        except IndexError:
            raise IpRange.DoesNotExist()


class IpRange(models.Model):
    """ IP ranges are stored in separate table, one row for each ip range.

        Each range might be associated with either country (for IP ranges outside of Russia and Ukraine)
        or country, region and city together.

        Ip range borders are `stored as long integers <http://publibn.boulder.ibm.com/doc_link/en_US/a_doc_lib/libs/commtrf2/inet_addr.htm>`_

    """
    start_ip = models.BigIntegerField(_('Ip range block begining, as integer'), db_index=True)
    end_ip = models.BigIntegerField(_('Ip range block ending, as integer'), db_index=True)
    country = models.ForeignKey(Country)
    region = models.ForeignKey(Region, null=True)
    city = models.ForeignKey(City, null=True)

    objects = IpRangeManager()

    class Meta:
        verbose_name = _(u'IP range')
        verbose_name_plural = _(u"IP ranges")


class abstractclassmethod(classmethod):
    """ Abstract classmethod decorator from python 3"""
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class AbsractModel(ABCMeta, ModelBase):
    pass


class GeoLocationFacade(models.Model):
    """ Interface for custom geographic models.
        Model represents a Facade pattern for concrete GeoIP models.
    """
    __metaclass__ = AbsractModel

    @abstractclassmethod
    def get_by_ip_range(cls, ip_range):
        """
        Return single model instance for given IP range.
        If no location matches the range, raises DoesNotExist exception.

        :param ip_range: User's IpRange to search for.
        :type ip_range: IpRange
        :return: GeoLocationFacade single object
        """
        return NotImplemented

    @abstractclassmethod
    def get_default_location(cls):
        """
        Return default location for cases where ip geolocation fails.

        :return: GeoLocationFacade
        """
        return NotImplemented

    @abstractclassmethod
    def get_available_locations(cls):
        """
        Return all locations available for users to select in frontend

        :return: GeoLocationFacade
        """
        return NotImplemented

    class Meta:
        abstract = True


class GeoLocationFascade(GeoLocationFacade):
    """ Old alias with a typo """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "GeoLocationFascade has been renamed to GeoLocationFacade, please update your code."
            "Alias will be removed in 0.3",
            DeprecationWarning
        )
        super(GeoLocationFascade, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True