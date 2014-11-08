from optparse import make_option
import os.path
import json
import random

from django.core.management import BaseCommand, CommandError

from omrs.models import Concept, ConceptName


def add_f(dictionary, key, value):
    if value is not None:
        dictionary[key] = value


class Command(BaseCommand):
    help = 'Extract concepts from OpenMRS database in the form of json'
    option_list = BaseCommand.option_list + (
        make_option('--concept_id',
                    action='store',
                    dest='concept_id',
                    default=None,
                    help='Database id for concept, if specified only export this one. e.g. 5839'),
        make_option('--count',
                    action='store',
                    dest='count',
                    default=None,
                    help='If specify, only export this many concepts. Useful for testing.'),
    )

    def export_concept(self, c):
        """
            Export one concept as json.

            :returns: json ready dictionary

        Issues:
        - description
            - missing desc type, locale_preferred

        """
        data = {}
        data['concept_class'] = c.concept_class.name
        data['datatype'] = c.datatype.name

        names = []
        for n in c.conceptname_set.all():
            names.append({
                'name': n.name,
                'name_type': n.concept_name_type,
                'locale': n.locale,
                'locale_preferred': n.locale_preferred,
                })
        data['names'] = names

        descs = []
        for n in c.conceptdescription_set.all():
            descs.append({
                'description': n.description,
                ## 'description_type': n.concept_name_type,
                'locale': n.locale,
                ## 'locale_preferred': n.locale_preferred,
                })
        data['descriptions'] = descs

        extras = []

        for e in c.conceptnumeric_set.all():
            d = {}
            add_f(d, 'hi_absolute', e.hi_absolute)
            add_f(d, 'hi_critical', e.hi_critical)
            add_f(d, 'hi_normal', e.hi_normal)
            add_f(d, 'low_absolute', e.low_absolute)
            add_f(d, 'low_critical', e.low_critical)
            add_f(d, 'low_normal', e.low_normal)
            add_f(d, 'units', e.units)
            add_f(d, 'precise', e.precise)
            extras.append(d)

        if c.conceptset_set is not None:
            for sc in c.conceptset_set.all():
                print sc.concept
                # put this to mapping

        data['extras'] = extras
        return data

    def export(self):
        """

        """
        if self.concept_id is not None:
            c = Concept.objects.get(concept_id=self.concept_id)
            data = self.export_concept(c)
            print json.dumps(data, indent=4)
            return

        for n, c in enumerate(Concept.objects.all()):
            if self.count is not None and n >= self.count:
                break

            data = self.export_concept(c)
            print json.dumps(data, indent=4)

    def handle(self, *args, **options):
        self.concept_id = options['concept_id']
        self.count = options['count']
        if self.count is not None:
            self.count = int(self.count)

        self.export()
