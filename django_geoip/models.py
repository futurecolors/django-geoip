# -*- coding: utf-8 -*-
import socket
import struct
from django.db import models
from django.utils.translation import ugettext_lazy as _
from management.commands import ipgeobase_settings

class Country(models.Model):
    code = models.CharField(_('country code'), max_length=2, primary_key=True)
    name = models.CharField(_('country name'), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class Region(models.Model):
    country = models.ForeignKey(Country, related_name='regions')
    name = models.CharField(_('region name'), max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        unique_together = (('country', 'name'), )


class City(models.Model):
    region = models.ForeignKey(Region, related_name='cities')
    name = models.CharField(_('city name'), max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = (('region', 'name'), )


class IpRangeManager(models.Manager):

    def by_ip(self, ip):
        """ Find the smallest range containing the given IP.
        """
        number = struct.unpack('!L', socket.inet_aton(ip))[0]
        try:
            return super(IpRangeManager, self).get_query_set()\
                                              .filter(start_ip__lte=number, end_ip__gte=number)\
                                              .order_by('end_ip', '-start_ip')[0]
        except IndexError:
            raise IpRange.DoesNotExist()


class IpRange(models.Model):
    """ Ip range borders are stored as long integers
        http://publibn.boulder.ibm.com/doc_link/en_US/a_doc_lib/libs/commtrf2/inet_addr.htm
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