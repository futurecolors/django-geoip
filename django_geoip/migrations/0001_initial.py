# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='city name')),
                ('latitude', models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True)),
            ],
            options={
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, verbose_name='country code', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='country name')),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IpRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_ip', models.BigIntegerField(verbose_name='Ip range block beginning, as integer', db_index=True)),
                ('end_ip', models.BigIntegerField(verbose_name='Ip range block ending, as integer', db_index=True)),
                ('city', models.ForeignKey(to='django_geoip.City', null=True)),
                ('country', models.ForeignKey(to='django_geoip.Country')),
            ],
            options={
                'verbose_name': 'IP range',
                'verbose_name_plural': 'IP ranges',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='region name')),
                ('country', models.ForeignKey(related_name='regions', to='django_geoip.Country')),
            ],
            options={
                'verbose_name': 'region',
                'verbose_name_plural': 'regions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('country', 'name')]),
        ),
        migrations.AddField(
            model_name='iprange',
            name='region',
            field=models.ForeignKey(to='django_geoip.Region', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(related_name='cities', to='django_geoip.Region'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together=set([('region', 'name')]),
        ),
    ]
