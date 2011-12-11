# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('django_geoip_country', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('django_geoip', ['Country'])

        # Adding model 'Region'
        db.create_table('django_geoip_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='regions', to=orm['django_geoip.Country'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('django_geoip', ['Region'])

        # Adding unique constraint on 'Region', fields ['country', 'name']
        db.create_unique('django_geoip_region', ['country_id', 'name'])

        # Adding model 'City'
        db.create_table('django_geoip_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cities', to=orm['django_geoip.Region'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
        ))
        db.send_create_signal('django_geoip', ['City'])

        # Adding unique constraint on 'City', fields ['region', 'name']
        db.create_unique('django_geoip_city', ['region_id', 'name'])

        # Adding model 'IpRange'
        db.create_table('django_geoip_iprange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_ip', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('end_ip', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_geoip.Country'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_geoip.Region'], null=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_geoip.City'], null=True)),
        ))
        db.send_create_signal('django_geoip', ['IpRange'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'City', fields ['region', 'name']
        db.delete_unique('django_geoip_city', ['region_id', 'name'])

        # Removing unique constraint on 'Region', fields ['country', 'name']
        db.delete_unique('django_geoip_region', ['country_id', 'name'])

        # Deleting model 'Country'
        db.delete_table('django_geoip_country')

        # Deleting model 'Region'
        db.delete_table('django_geoip_region')

        # Deleting model 'City'
        db.delete_table('django_geoip_city')

        # Deleting model 'IpRange'
        db.delete_table('django_geoip_iprange')


    models = {
        'django_geoip.city': {
            'Meta': {'unique_together': "(('region', 'name'),)", 'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cities'", 'to': "orm['django_geoip.Region']"})
        },
        'django_geoip.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'django_geoip.iprange': {
            'Meta': {'object_name': 'IpRange'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_geoip.City']", 'null': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_geoip.Country']"}),
            'end_ip': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_geoip.Region']", 'null': 'True'}),
            'start_ip': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'})
        },
        'django_geoip.region': {
            'Meta': {'unique_together': "(('country', 'name'),)", 'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['django_geoip.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['django_geoip']
