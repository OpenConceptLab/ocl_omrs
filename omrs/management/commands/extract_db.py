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
import json

from django.core.management import BaseCommand

from omrs.models import Concept, ConceptName, ConceptReferenceMap


def add_f(dictionary, key, value):
    if value is not None:
        dictionary[key] = value

source_directory = [
    ('IHTSDO', 'SNOMED-CT'),
    ('IHTSDO', 'SNOMED-NP'),
    ('WHO', 'ICD-10-WHO'),
    ('NLM', 'RxNORM'),
    ('NLM', 'RxNORM-Comb'),
    ('Regenstrief', 'LOINC'),
    ('WHO', 'ICD-10-WHO-NP'),
    ('WHO', 'ICD-10-WHO-2nd'),
    ('WHO', 'ICD-10-WHO-NP2'),
    ('HL7', 'HL-7-CVX'),
    ('PIH', 'PIH'),
    ('PIH', 'PIH-Malawi'),
    ('AMPATH', 'AMPATH'),
    ('Columbia', 'SNOMED-MVP'),
    ('OpenMRS', 'org.openmrs.module.mdrtb'),
    ('MVP', 'MVP-Amazon-Server-174'),
    ('IHTSDO', 'SNOMED-US'),
    ('HL7', 'HL7-2.x-Route-of-Administration'),
    ('3BT', '3BT'),
    ('WICC', 'ICPC2'),
    ('Columbia', 'CIEL'),
    ('CCAM', 'CCAM'),
    ('OpenMRS', 'org.openmrs.module.emrapi'),
    ('IMO', 'IMO-ProblemIT'),
    ('IMO', 'IMO-ProcedureIT'),
    ('VHA', 'NDF-RT-NUI'),
    ('FDA', 'FDA-Route-of-Administration'),
    ('NCI', 'NCI-Concept-Code'),
]


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
        make_option('--mapping',
                    action='store_true',
                    dest='mapping',
                    default=False,
                    help='Create mapping input file.'),
        make_option('--concept',
                    action='store_true',
                    dest='concept',
                    default=False,
                    help='Create concept input file.'),
        make_option('--raw',
                    action='store_true',
                    dest='raw',
                    default=False,
                    help='Format json output in raw mode for import.'),
        make_option('--retire',
                    action='store_true',
                    dest='retire_sw',
                    default=False,
                    help='If specify, output a list of retired concepts.'),
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
                'external_id': n.uuid,
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
        data['external_id'] = c.uuid

        extras = {}

        # No need to do this anymore
        # save the source UUID as extra
        # extras['external_id'] = c.uuid

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

        if self.do_mapping:
            self.handle_mapping(c)

        # handle concept sets
        # writes out:
        # 'concept_set, [source_id, dest_ids+]'
        if c.conceptset_set.count() > 0:
            self.concept_set_cnt += 1

            for sc in c.conceptset_set.all():
                if self.do_mapping:
                    self.internal_mapping('CONCEPT-SET', None,
                                          c, sc.concept.concept_id)

        # handle Q&A
        if c.question_answer.count() > 0:
            self.q_and_a_cnt += 1

            # this is a question for a Q&A set
            for ans in c.question_answer.all():

                if self.do_mapping:
                    self.internal_mapping('Q-AND-A', None,
                                          c, ans.answer_concept.concept_id)

        data['extras'] = extras
        return data

    def export(self):
        """
            Main loop to process all export, loop thru all concepts and
            export concept and mappings.
        """
        if self.concept_id is not None:
            # just do one export
            c = Concept.objects.get(concept_id=self.concept_id)
            data = self.export_concept(c)
            print json.dumps(data, indent=4)
            return

        q = Concept.objects.all()
        if self.count is not None:
            q = q.filter(concept_id__lte=self.count)
        for n, c in enumerate(q):

            data = self.export_concept(c)

            if not self.do_concept:
                continue

            if self.raw:
                print json.dumps(data)
            else:
                print json.dumps(data, indent=4)

    def write_mapping(self, data):
        """
        Output mapping data to output file.
        """
        if self.raw:
            self.mapping_file.write(json.dumps(data))
        else:
            self.mapping_file.write(json.dumps(data, indent=4))
        self.mapping_file.write('\n')

    def internal_mapping(self, map_type, external_id, concept, to_code):
        """
        """
        if self.count is not None and concept.concept_id > self.count:
                return

        data = {}
        data['map_type'] = map_type
        data['from_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
            self.org_id, self.source_id, concept.concept_id)

        if external_id is not None:
            data['external_id'] = external_id
        data['to_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
            self.org_id, self.source_id, to_code)

        self.write_mapping(data)

    def handle_mapping(self, concept):
        """
        """
        for r in concept.conceptreferencemap_set.all():

            data = {}
            data['map_type'] = r.map_type.name
            data['from_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
                self.org_id, self.source_id, concept.concept_id)

            data['external_id'] = r.uuid

            if r.concept_reference_term.concept_source.name == 'CIEL':

                # internal
                if str(concept.concept_id) == r.concept_reference_term.code:
                    # mapping to myself
                    continue

                self.internal_mapping(r.map_type.name,
                                      r.concept_reference_term.uuid,
                                      concept, r.concept_reference_term.code
                                      )
                return

            else:
                # external
                to_source_id = r.concept_reference_term.concept_source.name
                to_source_id = to_source_id.replace(' ', '-')

                to_org_id = None
                for o, s in source_directory:
                    if s == to_source_id:
                        to_org_id = o
                if to_org_id is None:
                    print 'Source %s not found in list.' % to_source_id
                    return

                # TODO
                if to_org_id == 'Columbia':
                    to_org_id = 'CIEL'

                data['to_source_url'] = '/orgs/%s/sources/%s/' % (
                    to_org_id, to_source_id)

                data['to_concept_code'] = r.concept_reference_term.code
                if r.concept_reference_term.name is not None:
                    data['to_concept_name'] = r.concept_reference_term.name

            self.write_mapping(data)

    def retire_only(self):
        """
            Just create retire concept list.
        """
        q = Concept.objects.all()
        if self.count is not None:
            q = q.filter(concept_id__lte=self.count)

            if c.retired:
                print c.concept_id

    def handle(self, *args, **options):
        self.concept_id = options['concept_id']
        self.count = options['count']
        self.raw = options['raw']
        self.do_mapping = options['mapping']
        self.do_concept = options['concept']
        self.do_retire = options['retire_sw']

        self.org_id = 'CIEL'
        self.source_id = 'CIEL'

        if self.count is not None:
            self.count = int(self.count)

        self.q_and_a_cnt = 0
        self.concept_set_cnt = 0
        self.total = 0

        if self.do_retire:
            self.retire_only()
            return

        if self.do_mapping:
            self.mapping_file = open('mapping.txt', 'w')

        self.export()

        # print 'Total concepts processed %d' % self.total
        # print 'Q & A processed %d' % self.q_and_a_cnt
        # print 'Concept sets processed %d' % self.concept_set_cnt
