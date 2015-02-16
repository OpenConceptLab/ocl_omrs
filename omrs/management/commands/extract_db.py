"""
    command to create JSON for import OMRS data into OCL.

    normally run this to do full export, output to stdout:

        manage.py extract_db --raw


    In addition if you need to create inputs to mapping import,
    use the --mapping argument, the mapping data will always
    write to a file called mapping.txt

        manage.py extract_db --mapping

"""
from optparse import make_option
import os.path
import json

from django.core.management import BaseCommand, CommandError

from omrs.models import Concept, ConceptName, ConceptReferenceMap


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
        make_option('--stats',
                    action='store_true',
                    dest='stats',
                    default=False,
                    help='Just print out statistics.'),
        make_option('--mapping',
                    action='store_true',
                    dest='mapping',
                    default=False,
                    help='Create mapping input file.'),
        make_option('--raw',
                    action='store_true',
                    dest='raw',
                    default=False,
                    help='Format json output in raw mode for import.'),
    )

    def export_concept(self, c):
        """
            Export one concept as json.

            :param c: is one concept object from OMRS database.
            :returns: json ready dictionary

        Issues:
        - description
            - missing desc type, locale_preferred
        - missing drug table

        """
        self.total += 1

        data = {}
        data['id'] = c.concept_id
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
                #  'description_type': n.concept_name_type,
                'locale': n.locale,
                #  'locale_preferred': n.locale_preferred,
            })
        data['descriptions'] = descs

        extras = {}

        # save the source UUID as extra
        extras['external_id'] = c.uuid

        # if the concept is of numeric type,
        # map concept's numeric type data as extras
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
            extras.update(d)

        if self.mapping:
            self.handle_mapping(c)

        # handle concept sets
        # writes out:
        # 'concept_set, [source_id, dest_ids+]'
        if c.conceptset_set.count() > 0:
            self.concept_set_cnt += 1
            ids = [str(c.concept_id)]
            for sc in c.conceptset_set.all():
                ids.append(str(sc.concept.concept_id))
            if self.mapping:
                self.mapping_file.write('concept_set ')
                self.mapping_file.write(' '.join(ids))
                self.mapping_file.write('\n')

        # handle Q&A
        if c.question_answer.count() > 0:
            self.q_and_a_cnt += 1

            ids = [str(c.concept_id)]

            # this is a question for a Q&A set
            for ans in c.question_answer.all():
                pass
                # print ans.answer_concept
                ids.append(str(ans.answer_concept.concept_id))
            if self.mapping:
                self.mapping_file.write('q_and_a ')
                self.mapping_file.write(' '.join(ids))
                self.mapping_file.write('\n')
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

        # for n, c in enumerate(Concept.objects.filter(question_answer__isnull=False)):
        for n, c in enumerate(Concept.objects.all()):

            if self.count is not None and n >= self.count:
                break

            data = self.export_concept(c)
            if self.stats:
                continue

            if self.raw:
                print json.dumps(data)
            else:
                print json.dumps(data, indent=4)

    def handle_mapping(self, concept):
        """
        """
        for r in concept.conceptreferencemap_set.all():
            fields = [r.map_type.name,
                      r.concept_reference_term.code,
                      r.concept_reference_term.concept_source.name]

            self.mapping_file.write('internal %s ' % concept.concept_id)
            self.mapping_file.write(','.join(fields))
            self.mapping_file.write('\n')

    def handle(self, *args, **options):
        self.concept_id = options['concept_id']
        self.stats = options['stats']
        self.count = options['count']
        self.raw = options['raw']
        self.mapping = options['mapping']

        if self.count is not None:
            self.count = int(self.count)

        self.q_and_a_cnt = 0
        self.concept_set_cnt = 0
        self.total = 0

        if self.mapping:
            self.mapping_file = open('mapping.txt', 'w')

        self.export()

        if self.stats:
            print 'Total concepts processed %d' % self.total
            print 'Q & A processed %d' % self.q_and_a_cnt
            print 'Concept sets processed %d' % self.concept_set_cnt
