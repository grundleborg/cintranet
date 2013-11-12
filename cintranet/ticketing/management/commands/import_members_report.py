import csv
import datetime
import codecs
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import utc

from ticketing import models

START_DATE = datetime.datetime(2013, 9, 28, tzinfo=utc)
END_DATE = datetime.datetime(2014, 06, 28, tzinfo=utc)
AUTOMATIC_ENTITLEMENTS = [
    (models.TicketTemplate, 3, {
        'remaining_uses': 1,
        'start_date': START_DATE,
        'end_date': END_DATE
    }), # free ticket
    (models.TicketTemplate, 1, {
        'start_date': START_DATE,
        'end_date': END_DATE
    }),
]

##### FROM http://docs.python.org/2/library/csv.html#csv-examples
class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('cp850').decode('iso8859-1').encode("utf-8")
class UnicodeCsvReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num

class UnicodeDictCsvReader(csv.DictReader):
    def __init__(self,
                f, fieldnames=None, restkey=None, restval=None, dialect="excel",
                encoding="utf-8",
                *args, **kwargs
            ):
        csv.DictReader.__init__(
            self,
            f, fieldnames, restkey, restval, dialect, *args, **kwargs
        )
        self.reader = UnicodeCsvReader(f, dialect, encoding, *args, **kwargs)

class Command(BaseCommand):
    args = 'path_to_members_report'
    help = 'Imports the specified Members Report into the database'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            raise CommandError(u"Must pass the path to Members_Report.csv")
        elif len(args) > 1:
            raise CommandError(u"Too many arguments!")

        entitlements = []
        from django.contrib.contenttypes.models import ContentType
        for ent_model, ent_pk, ent_kwargs in AUTOMATIC_ENTITLEMENTS:
            entitlements.append((
                ContentType.objects.get_for_model(ent_model),
                ent_pk,
                ent_kwargs
            ))

        members_report_path, = args
        with open(members_report_path, 'rb') as csvfile:
            csvr = UnicodeDictCsvReader(csvfile, encoding='iso8859-1')

            count_total = 0
            count_errored = 0
            count_already_exist = 0
            count_created = 0

            count_created_ents = 0
            count_already_exist_created_ents = 0
            count_total_ents_created = 0

            for member in csvr:
                try:
                    _, created, ents_created = self.handle_member(member, entitlements)
                except Exception, ex:
                    count_total += 1
                    count_errored += 1
                    traceback.print_exc(file=self.stderr)
                    continue

                count_total += 1
                if created:
                    count_created += 1
                else:
                    count_already_exist += 1
                if ents_created != 0:
                    count_created_ents += 1
                    count_total_ents_created += ents_created
                if not created and ents_created != 0:
                    count_already_exist_created_ents += 1

            self.stdout.write("")
            self.stdout.write("RESULTS")
            self.stdout.write("-------")
            self.stdout.write("")
            self.stdout.write("CATEGORY\tMEMBER COUNT")
            self.stdout.write("Created:\t{}".format(count_created))
            self.stdout.write("Existing:\t{}".format(count_already_exist))
            self.stdout.write("Errored:\t{}".format(count_errored))
            self.stdout.write("Total:\t\t{}".format(count_total))
            self.stdout.write("")
            self.stdout.write("CATEGORY\t\t\tCOUNT")
            self.stdout.write("Created for <n> members:\t{}".format(count_created_ents))
            self.stdout.write("...where member existed:\t{}".format(count_already_exist_created_ents))
            self.stdout.write("Total created:\t\t\t{}".format(count_total_ents_created))

    def handle_member(self, csv_row, entitlements):
        # massage the data set
        cid = csv_row['CID']
        name = u"{} {}".format(csv_row['First Name'], csv_row['Last Name'])
        note = u"Bought membership on {} (order no {})".format(
            csv_row['Date'],
            csv_row['Order No']
        )
        email = csv_row['Email']
        username = csv_row['Login']
        punter_type = models.PUNTER_FULL if cid != '' else models.PUNTER_ASSOCIATE

        filter_on = {}
        if cid != '':
            filter_on = {'cid': cid}
            self.stdout.write(u'Handling {} (CID: {}, username: {})'.format(name, cid, username))
        else:
            filter_on = {'name': name}
            self.stdout.write(u'Handling {} (associate/life member)'.format(name))

        obj, created = models.Punter.objects.get_or_create(
            defaults={
                'cid': cid,
                'name': name,
                'comment': note,
                'email': email,
                'login': username,
                'punter_type': punter_type
            },
            **filter_on
        )

        entitlements_created = 0
        # check if entitlements already exist
        for ent_ct, ent_id, ent_kwargs in entitlements:
            _, c = models.Entitlement.objects.get_or_create(
                punter=obj,
                entitled_to_type=ent_ct,
                entitled_to_id=ent_id,
                defaults=ent_kwargs
            )
            if c:
                entitlements_created += 1

        return obj, created, entitlements_created