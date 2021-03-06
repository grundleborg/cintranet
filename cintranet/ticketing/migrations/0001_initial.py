# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Punter'
        db.create_table(u'ticketing_punter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('punter_type', self.gf('model_utils.fields.StatusField')(default='full', max_length=100, no_check_for_status=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('cid', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
            ('login', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
            ('swipecard', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default='', max_length=256, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'ticketing', ['Punter'])

        # Adding model 'Film'
        db.create_table(u'ticketing_film', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'ticketing', ['Film'])

        # Adding model 'Showing'
        db.create_table(u'ticketing_showing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.Film'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'ticketing', ['Showing'])

        # Adding model 'EventType'
        db.create_table(u'ticketing_eventtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=128)),
        ))
        db.send_create_signal(u'ticketing', ['EventType'])

        # Adding model 'Event'
        db.create_table(u'ticketing_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'ticketing', ['Event'])

        # Adding M2M table for field showings on 'Event'
        m2m_table_name = db.shorten_name(u'ticketing_event_showings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'ticketing.event'], null=False)),
            ('showing', models.ForeignKey(orm[u'ticketing.showing'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'showing_id'])

        # Adding M2M table for field event_types on 'Event'
        m2m_table_name = db.shorten_name(u'ticketing_event_event_types')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'ticketing.event'], null=False)),
            ('eventtype', models.ForeignKey(orm[u'ticketing.eventtype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'eventtype_id'])

        # Adding model 'BaseTicketInfo'
        db.create_table(u'ticketing_baseticketinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('online_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('sell_online', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sell_on_the_door', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('general_availability', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sale_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('box_office_return_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'ticketing', ['BaseTicketInfo'])

        # Adding model 'TicketTemplate'
        db.create_table(u'ticketing_tickettemplate', (
            (u'baseticketinfo_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ticketing.BaseTicketInfo'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'ticketing', ['TicketTemplate'])

        # Adding M2M table for field event_type on 'TicketTemplate'
        m2m_table_name = db.shorten_name(u'ticketing_tickettemplate_event_type')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tickettemplate', models.ForeignKey(orm[u'ticketing.tickettemplate'], null=False)),
            ('eventtype', models.ForeignKey(orm[u'ticketing.eventtype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tickettemplate_id', 'eventtype_id'])

        # Adding model 'TicketType'
        db.create_table(u'ticketing_tickettype', (
            (u'baseticketinfo_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ticketing.BaseTicketInfo'], unique=True, primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.TicketTemplate'], null=True, blank=True)),
        ))
        db.send_create_signal(u'ticketing', ['TicketType'])

        # Adding model 'Entitlement'
        db.create_table(u'ticketing_entitlement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('punter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entitlements', to=orm['ticketing.Punter'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('remaining_uses', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ticketing', ['Entitlement'])

        # Adding M2M table for field entitled_to on 'Entitlement'
        m2m_table_name = db.shorten_name(u'ticketing_entitlement_entitled_to')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entitlement', models.ForeignKey(orm[u'ticketing.entitlement'], null=False)),
            ('baseticketinfo', models.ForeignKey(orm[u'ticketing.baseticketinfo'], null=False))
        ))
        db.create_unique(m2m_table_name, ['entitlement_id', 'baseticketinfo_id'])

        # Adding model 'Ticket'
        db.create_table(u'ticketing_ticket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ticket_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tickets', to=orm['ticketing.TicketType'])),
            ('punter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tickets', null=True, to=orm['ticketing.Punter'])),
            ('entitlement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entitlements', null=True, to=orm['ticketing.Entitlement'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('model_utils.fields.StatusField')(default='live', max_length=100, no_check_for_status=True, db_index=True)),
        ))
        db.send_create_signal(u'ticketing', ['Ticket'])


    def backwards(self, orm):
        # Deleting model 'Punter'
        db.delete_table(u'ticketing_punter')

        # Deleting model 'Film'
        db.delete_table(u'ticketing_film')

        # Deleting model 'Showing'
        db.delete_table(u'ticketing_showing')

        # Deleting model 'EventType'
        db.delete_table(u'ticketing_eventtype')

        # Deleting model 'Event'
        db.delete_table(u'ticketing_event')

        # Removing M2M table for field showings on 'Event'
        db.delete_table(db.shorten_name(u'ticketing_event_showings'))

        # Removing M2M table for field event_types on 'Event'
        db.delete_table(db.shorten_name(u'ticketing_event_event_types'))

        # Deleting model 'BaseTicketInfo'
        db.delete_table(u'ticketing_baseticketinfo')

        # Deleting model 'TicketTemplate'
        db.delete_table(u'ticketing_tickettemplate')

        # Removing M2M table for field event_type on 'TicketTemplate'
        db.delete_table(db.shorten_name(u'ticketing_tickettemplate_event_type'))

        # Deleting model 'TicketType'
        db.delete_table(u'ticketing_tickettype')

        # Deleting model 'Entitlement'
        db.delete_table(u'ticketing_entitlement')

        # Removing M2M table for field entitled_to on 'Entitlement'
        db.delete_table(db.shorten_name(u'ticketing_entitlement_entitled_to'))

        # Deleting model 'Ticket'
        db.delete_table(u'ticketing_ticket')


    models = {
        u'ticketing.baseticketinfo': {
            'Meta': {'object_name': 'BaseTicketInfo'},
            'box_office_return_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'general_availability': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sale_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sell_on_the_door': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sell_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ticketing.entitlement': {
            'Meta': {'object_name': 'Entitlement'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entitled_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'entitlements'", 'symmetrical': 'False', 'to': u"orm['ticketing.BaseTicketInfo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlements'", 'to': u"orm['ticketing.Punter']"}),
            'remaining_uses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ticketing.event': {
            'Meta': {'object_name': 'Event'},
            'event_types': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_types'", 'null': 'True', 'to': u"orm['ticketing.EventType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'showings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'symmetrical': 'False', 'to': u"orm['ticketing.Showing']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.eventtype': {
            'Meta': {'object_name': 'EventType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'})
        },
        u'ticketing.film': {
            'Meta': {'object_name': 'Film'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'ticketing.punter': {
            'Meta': {'object_name': 'Punter'},
            'cid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'punter_type': ('model_utils.fields.StatusField', [], {'default': "'full'", 'max_length': '100', u'no_check_for_status': 'True', 'db_index': 'True'}),
            'swipecard': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'})
        },
        u'ticketing.showing': {
            'Meta': {'object_name': 'Showing'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'entitlement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlements'", 'null': 'True', 'to': u"orm['ticketing.Entitlement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'null': 'True', 'to': u"orm['ticketing.Punter']"}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'live'", 'max_length': '100', u'no_check_for_status': 'True', 'db_index': 'True'}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': u"orm['ticketing.TicketType']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.tickettemplate': {
            'Meta': {'object_name': 'TicketTemplate', '_ormbases': [u'ticketing.BaseTicketInfo']},
            u'baseticketinfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ticketing.BaseTicketInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'event_type': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ticket_templates'", 'symmetrical': 'False', 'to': u"orm['ticketing.EventType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'ticketing.tickettype': {
            'Meta': {'object_name': 'TicketType', '_ormbases': [u'ticketing.BaseTicketInfo']},
            u'baseticketinfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ticketing.BaseTicketInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Event']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.TicketTemplate']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ticketing']