import itertools
import re

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from django.conf import settings

from model_utils.managers import InheritanceManager
from model_utils.fields import StatusField
from model_utils import Choices
from tmdbsimple import TMDB

Q = models.Q
tmdb = TMDB(settings.TMDB_API_KEY)
_tmdb_conf = None
tmdb_url_re = re.compile(r'^https?://[a-z\.]+/movie/(?P<tmdb_id>\d+)-.*$')

def tmdb_config():
    global _tmdb_conf
    if _tmdb_conf is None:
        _tmdb_conf = tmdb.Configuration()
        _tmdb_conf.info()
    return _tmdb_conf

def tmdb_construct_poster(img_bit, size='original'):
    c = tmdb_config()
    return c.images['base_url'] + size + img_bit

class Punter(models.Model):
    STATUS = Choices('full', 'associate', 'public')

    punter_type = StatusField(db_index=True)
    name = models.CharField(max_length=256, default="", null=False, blank=True)
    cid = models.CharField(max_length=16, default="", null=False, blank=True)
    login = models.CharField(max_length=16, default="", null=False, blank=True)
    swipecard = models.CharField(max_length=64, default="", null=False, blank=True)
    email = models.EmailField(max_length=256, default="", null=False, blank=True)
    comment = models.TextField(null=False, default="", blank=True)

    def __unicode__(self):
        return self.name

    def available_tickets(self, events, at_time=None, on_door=True, online=False):
        return TicketType.objects.filter(
            Q(event__in=events) &
            (
                Q(
                    general_availability=True,
                    sell_on_the_door=on_door,
                    sell_online=online,
                ) | Q(
                    Q(
                        EntitlementDetail.valid_q_obj("entitlements__entitlement_detail__", at_time=at_time),
                        entitlements__entitlement_detail__punter=self,
                    ) | Q(
                        EntitlementDetail.valid_q_obj("template__entitlements__entitlement_detail__", at_time=at_time),
                        template__entitlements__entitlement_detail__punter=self,
                    ),
                    general_availability=False,
                )
            )
        )

class Film(models.Model):
    tmdb_id = models.PositiveIntegerField(null=True)
    imdb_id = models.CharField(max_length=20, null=False, blank=True, default="")

    name = models.CharField(max_length=256, default="", null=False, blank=False)
    description = models.TextField(default="", null=False, blank=True)

    poster_url = models.URLField(blank=True, null=False, default="")

    def __unicode__(self):
        return self.name

    @classmethod
    def from_tmdb(cls, tmdb_id):
        if 'themoviedb.org' in str(tmdb_id):
            # it looks like a URL...
            tmdb_match = tmdb_url_re.search(tmdb_id)
            if not tmdb_match:
                return None
            tmdb_id = tmdb_match.groupdict().get('tmdb_id', None)
        self = cls(tmdb_id=int(tmdb_id))
        self.update_tmdb()
        return self

    def update_tmdb(self):
        movie = tmdb.Movies(self.tmdb_id)
        movie.info()
        self.name = movie.title
        self.description = movie.overview
        self.imdb_id = movie.imdb_id
        self.poster_url = tmdb_construct_poster(movie.poster_path)

    def update_imdb(self):
        pass

    def update_remote(self):
        if self.tmdb_id is not None:
            self.update_tmdb()
        if self.imdb_id != "":
            self.update_imdb()
        self.save()

class Showing(models.Model):
    name = models.CharField(max_length=300, default="", null=False, blank=False)
    film = models.ForeignKey(Film, null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.start_time)

    def save(self, *args, **kwargs):
        old_pk = self.pk
        r = super(Showing, self).save(*args, **kwargs)
        new_pk = self.pk

        is_new = old_pk != new_pk
        if is_new:
            ev = Event(
                name=self.name,
                start_time=self.start_time
            )
            ev.event_types = [EventType.objects.get(pk=settings.TICKETING_STANDARD_EVENT_TYPE)]
            ev.save()
            ev.showings.add(self)
        return r




class EventType(models.Model):
    name = models.CharField(max_length=128, default="", null=False, blank=False)

    def __unicode__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=300, default="", null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    showings = models.ManyToManyField(Showing, null=False, related_name='events')
    event_types = models.ManyToManyField(EventType, null=True, related_name='event_types')

    def create_ticket_types_by_event_types(self):
        event_types = self.event_types.prefetch_related('ticket_templates').all()
        ticket_templates = [z.ticket_templates.all() for z in event_types]
        ticket_templates = itertools.chain.from_iterable(ticket_templates)
        for ticket_template in ticket_templates:
            TicketType.from_template(ticket_template, self).save()

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.start_time)

class BaseTicketInfo(models.Model):
    online_description = models.TextField(null=False, default="", blank=True)
    sell_online = models.BooleanField(default=False)
    sell_on_the_door = models.BooleanField(default=True)
    general_availability = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        decimal_places=2, max_digits=5,
        help_text='This is the price at which tickets are sold - the price punters will pay'
    )
    box_office_return_price = models.DecimalField(
        decimal_places=2, max_digits=5,
        help_text="""This is the ex-VAT price reported on the BOR for each film!"""
    )
    name = models.CharField(max_length=128, null=False, blank=False)

    objects = InheritanceManager()

    def __unicode__(self):
        return self.name


class TicketTemplate(BaseTicketInfo):
    event_type = models.ManyToManyField(EventType, related_name='ticket_templates')

class TicketType(BaseTicketInfo):
    event = models.ForeignKey(Event)

    template = models.ForeignKey(TicketTemplate, blank=True, null=True)

    def __unicode__(self):
        return u"{} (for {})".format(self.name, unicode(self.event))

    @classmethod
    def from_template(cls, template, event):
        props = (
            'online_description',
            'sell_online',
            'sell_on_the_door',
            'general_availability',
            'sale_price',
            'box_office_return_price'
        )
        tt = cls(
            template=template,
            event=event
        )
        tt.name = '{} for {}'.format(template.name, event.name)
        for prop in props:
            setattr(tt, prop, getattr(template, prop))
        return tt

    def __unicode__(self):
        return u"{} for {}".format(self.name, self.event)

class EntitlementDetail(models.Model):
    punter = models.ForeignKey(Punter, related_name='entitlement_details')
    entitlement = models.ForeignKey('Entitlement', related_name='entitlement_details')
    created_on = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    remaining_uses = models.PositiveIntegerField(null=True, blank=True)

    def valid(self, at_time=None):
        if self.remaining_uses is not None and self.remaining_uses <= 0:
            # all used up
            return False

        # delegate it to the base entitlement validity checker
        return self.entitlement.valid()
    valid.boolean = True

    @staticmethod
    def valid_q_obj(prefix="", at_time=None):
        remaining_uses_q_kw = Q(**{
            prefix + "remaining_uses__isnull": True
        }) | Q(**{
            prefix + "remaining_uses__gt": 0
        })

        return remaining_uses_q_kw & Entitlement.valid_q_obj(prefix + "entitlement__", at_time)

    def name(self):
        return self.entitlement.name

class Entitlement(models.Model):
    punters = models.ManyToManyField(Punter, related_name='entitlements', through=EntitlementDetail)
    name = models.CharField(max_length=255, null=False, blank=False, db_index=True, unique=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    entitled_to = models.ManyToManyField(BaseTicketInfo, related_name='entitlements')

    def valid(self, at_time=None):
        at_time = at_time or now()

        if self.start_date is not None and self.start_date > at_time:
            # not yet valid
            return False

        if self.end_date is not None and self.end_date < at_time:
            # passed end of validity
            return False

        return True
    valid.boolean = True

    @staticmethod
    def valid_q_obj(prefix="", at_time=None):
        at_time = at_time or now()

        start_date_q_kw = Q(**{
            prefix + "start_date__isnull": True
        }) | Q(**{
            prefix + "start_date__lt": at_time
        })

        end_date_q_kw = Q(**{
            prefix + "end_date__isnull": True
        }) | Q(**{
            prefix + "end_date__gt": at_time
        })

        return start_date_q_kw & end_date_q_kw

    def __unicode__(self):
        return u"{} ({})".format(
            self.name, 'valid' if self.valid() else 'invalid'
        )

class Ticket(models.Model):
    STATUS = Choices('live', 'void', 'refunded')

    ticket_type = models.ForeignKey(TicketType, related_name='tickets', null=False)

    punter = models.ForeignKey(Punter, related_name='tickets', null=True)
    entitlement = models.ForeignKey(Entitlement, related_name='entitlements', null=True)

    timestamp = models.DateTimeField(null=False, blank=False)
    status = StatusField(db_index=True)

    def __unicode__(self):
        return u"{} ticket for {}".format(self.status, self.ticket_type)
