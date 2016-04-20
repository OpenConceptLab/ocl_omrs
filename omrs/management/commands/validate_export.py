"""
Command to validate an OCL source version export against an OpenMRS dictionary stored in Mysql.

TODO: Implement "deep" comparison for both concepts and mappings -- start with checking only active status

"""
import json
from django.core.management import BaseCommand
from optparse import make_option
from omrs.models import (Concept, ConceptReferenceMap, ConceptAnswer, ConceptSet)
from omrs.management.commands import OclOpenmrsHelper


class Command(BaseCommand):
    """
    Validate an OCL export against an OpenMRS dictionary stored in Mysql.
    """

    # Constants
    MISSING_IN_OCL = 1
    MISSING_IN_MYSQL = 2

    # Command attributes
    help = 'Validate an OCL export against an OpenMRS dictionary stored in Mysql.'
    option_list = BaseCommand.option_list + (
        make_option('--export',
                    action='store',
                    dest='ocl_export_filename',
                    default=None,
                    help='OCL export filename'),
        make_option('--ignore_retired_mappings',
                    action='store_true',
                    dest='ignore_retired_mappings',
                    default=False,
                    help='Retired mappings in OCL are not included in the comparison if set to True'),
    )


    ## COMMAND LINE HANDLER AND ARGUMENT VALIDATION

    def handle(self, *args, **options):
        """
        This method is called first directly from the command line, handles options, and
        initiates the validation process.
        """

        # Get command line arguments
        self.ocl_export_filename = options['ocl_export_filename']
        self.ignore_retired_mappings = options['ignore_retired_mappings']
        self.verbosity = int(options['verbosity'])

        # Option debug output
        if self.verbosity >= 2:
            print 'COMMAND LINE OPTIONS:\n', options

        # Load the OCL export file into memory
        # NOTE: This will only work if it can fit into memory -- explore streaming partial loads
        export_text = open(self.ocl_export_filename).read()
        loaded_json = json.loads(export_text)
        export_text = None
        if 'concepts' not in loaded_json:
            loaded_json['concepts'] = []
        if 'mappings' not in loaded_json:
            loaded_json['mappings'] = []

        # Validate the concepts and mappings in the file
        self.validate_export(loaded_json)

    def validate_export(self, data):
        self.validate_concepts(data)
        self.validate_mappings(data)

    def validate_concepts(self, data):

        # Create an array of concept IDs that are in the mysql db
        print '\nCONCEPT COUNT COMPARISON:'
        id_comparison = {
            self.MISSING_IN_OCL:{},
            self.MISSING_IN_MYSQL:{},
        }
        for c_mysql in Concept.objects.raw('SELECT concept_id FROM concept'):
            id_comparison[self.MISSING_IN_OCL][str(c_mysql.concept_id)] = 0
        count_mysql = len(id_comparison[self.MISSING_IN_OCL])

        # Perform count comparison
        count_ocl = len(data['concepts'])
        if count_ocl == count_mysql:
            print 'Concept count comparison: OCL %s == MYSQL %s\n' % (count_ocl, count_mysql)
        else:
            print 'Concept count comparison: OCL %s != MYSQL %s\n' % (count_ocl, count_mysql)

        # Perform an ID comparison
        print '\nVALIDATING CONCEPTS:'
        cnt = 0
        for c_ocl in data['concepts']:
            # Display progress bar
            cnt += 1
            if (cnt % 1000) == 1:
                print 'Validating %s to %s of %s concepts...' % (cnt, cnt - 1 + 1000, count_ocl)

            # Do the comparison
            if c_ocl['id'] in id_comparison[self.MISSING_IN_OCL]:
                del id_comparison[self.MISSING_IN_OCL][c_ocl['id']]
            else:
                id_comparison[self.MISSING_IN_MYSQL][c_ocl['id']] = 0
                if self.verbosity >= 2: print 'Concept %s exists in OCL but is missing in Mysql: %s' % (c_ocl['id'], c_ocl)

        # Output summary of results
        print '\n\nCONCEPT VALIDATION SUMMARY:'
        print '\n%s concept IDs missing in OCL:\n' % len(id_comparison[self.MISSING_IN_OCL])
        print id_comparison[self.MISSING_IN_OCL]
        print '\n%s concept IDs missing in MySQL:\n' % len(id_comparison[self.MISSING_IN_MYSQL])
        print id_comparison[self.MISSING_IN_MYSQL]

        # For IDs missing in MySQL, check if they are duplicated in the export
        missing_ids = id_comparison[self.MISSING_IN_MYSQL].copy()
        if missing_ids:
            for c_ocl in data['concepts']:
                if c_ocl['id'] in missing_ids:
                    missing_ids[c_ocl['id']] += 1
                    print c_ocl
            print '\nChecking for duplicate IDs in export:\n'
            num_duplicates = 0
            for c_id in missing_ids:
                if missing_ids[c_id]:
                    print '%s: %s duplicates found in export file\n' % (c_id, missing_ids[c_id])
                    num_duplicates += 1
            if not num_duplicates:
                print 'No duplicates found in export file\n'

        # Perform deep comparison
        print '\nSkipping deep comparison of concepts...\n'

        return

    def validate_mappings(self, data):
        """
        OpenMRS has 3 different objects that get stored as mappings in OCL: Reference Maps,
        Q-and-A, and Concept Sets. This script iterates through each of these sets of objects
        and compares against the records in OCL.
        """

        # Count objects in OCL
        print '\nMAPPING COUNT COMPARISON:'
        cnt_ocl_mapref = cnt_ocl_qanda = cnt_ocl_conceptset = cnt_ocl_retired_maps = 0
        for m_ocl in data['mappings']:
            map_type = str(m_ocl['map_type'])
            retired = m_ocl['retired']
            if retired:
                cnt_ocl_retired_maps += 1
            if (retired and not self.ignore_retired_mappings) or not retired:
                if map_type == OclOpenmrsHelper.MAP_TYPE_Q_AND_A:
                    cnt_ocl_qanda += 1
                elif map_type == OclOpenmrsHelper.MAP_TYPE_CONCEPT_SET:
                    cnt_ocl_conceptset += 1
                else:
                    cnt_ocl_mapref += 1
        cnt_ocl_total = cnt_ocl_mapref + cnt_ocl_qanda + cnt_ocl_conceptset
        cnt_ocl_total_with_retired = (cnt_ocl_total + cnt_ocl_retired_maps) if self.ignore_retired_mappings else cnt_ocl_total

        # Count objects in MySQL
        cnt_mysql_mapref = ConceptReferenceMap.objects.exclude(concept_reference_term__concept_source__name='CIEL').count()
        cnt_mysql_qanda = ConceptAnswer.objects.count()
        cnt_mysql_conceptset = ConceptSet.objects.count()
        cnt_mysql_total = cnt_mysql_mapref + cnt_mysql_qanda + cnt_mysql_conceptset

        # Count comparison
        print '%s total mappings in OCL Export file, including %s retired mappings.' % (cnt_ocl_total_with_retired, cnt_ocl_retired_maps)
        if self.ignore_retired_mappings:
            print '%s active mappings used in the comparison ("ignore_retired_mappings" flag set)' % cnt_ocl_total
        else:
            print 'Both active and inactive mappings used in the comparison (set "ignore_retired_mappings" flag to exclude retired mappings)'
        if cnt_ocl_total == cnt_mysql_total:
            print 'Count comparison of all mappings: OCL %s == MYSQL %s' % (cnt_ocl_total, cnt_mysql_total)
        else:
            print 'Count comparison of all mappings: OCL %s != MYSQL %s' % (cnt_ocl_total, cnt_mysql_total)
        if cnt_ocl_mapref == cnt_mysql_mapref:
            print 'Count comparison of reference maps: OCL %s == MYSQL %s' % (cnt_ocl_mapref, cnt_mysql_mapref)
        else:
            print 'Count comparison of reference maps: OCL %s != MYSQL %s' % (cnt_ocl_mapref, cnt_mysql_mapref)
        if cnt_ocl_qanda == cnt_mysql_qanda:
            print 'Count comparison of Q-AND-A: OCL %s == MYSQL %s' % (cnt_ocl_qanda, cnt_mysql_qanda)
        else:
            print 'Count comparison of Q-AND-A: OCL %s != MYSQL %s' % (cnt_ocl_qanda, cnt_mysql_qanda)
        if cnt_ocl_conceptset == cnt_mysql_conceptset:
            print 'Count comparison of Concept Sets: OCL %s == MYSQL %s' % (cnt_ocl_conceptset, cnt_mysql_conceptset)
        else:
            print 'Count comparison of Concept Sets: OCL %s != MYSQL %s' % (cnt_ocl_conceptset, cnt_mysql_conceptset)

        # Create an array of key comparison data from mappings in Mysql
        self.qanda_comparison = {
            self.MISSING_IN_OCL:[],
            self.MISSING_IN_MYSQL:[],
        }
        self.conceptset_comparison = {
            self.MISSING_IN_OCL:[],
            self.MISSING_IN_MYSQL:[],
        }
        self.refmap_comparison = {
            self.MISSING_IN_OCL:[],
            self.MISSING_IN_MYSQL:[],
        }

        # Populate "missing_in_ocl" arrays with everything from omrs
        for refmap_mysql in ConceptReferenceMap.objects.exclude(concept_reference_term__concept_source__name='CIEL'):
            self.refmap_comparison[self.MISSING_IN_OCL].append(refmap_mysql.concept_map_id)
        for qanda_mysql in ConceptAnswer.objects.raw('SELECT concept_answer_id FROM concept_answer'):
            self.qanda_comparison[self.MISSING_IN_OCL].append(qanda_mysql.concept_answer_id)
        for conceptset_mysql in ConceptSet.objects.raw('select concept_set_id from concept_set'):
            self.conceptset_comparison[self.MISSING_IN_OCL].append(conceptset_mysql.concept_set_id)

        # Iterate through OCL data and directly compare
        print '\nVALIDATING MAPPINGS:'
        cnt = 0
        for m_ocl in data['mappings']:

            # Skip retired mappings entirely if flag is set
            if self.ignore_retired_mappings and m_ocl['retired']:
                continue

            # Display progress info
            cnt += 1
            if (cnt % 1000) == 1: print 'Validating %s to %s of %s mappings...' % (cnt, cnt - 1 + 1000, cnt_ocl_total)

            # Determine the type of comparison to perform, compare, and handle results
            ocl_map_type = str(m_ocl['map_type'])
            if ocl_map_type == OclOpenmrsHelper.MAP_TYPE_Q_AND_A and m_ocl['to_source_name'] == 'CIEL':
                mysql_matching_qanda_id = self.validate_qanda(m_ocl)
                if mysql_matching_qanda_id:
                    self.qanda_comparison[self.MISSING_IN_OCL].remove(mysql_matching_qanda_id)
                else:
                    self.qanda_comparison[self.MISSING_IN_MYSQL].append(m_ocl['id'])
                    if self.verbosity >= 2: print 'Missing qanda in MySQL: %s\n' % m_ocl
            elif ocl_map_type == OclOpenmrsHelper.MAP_TYPE_CONCEPT_SET and m_ocl['to_source_name'] == 'CIEL':
                mysql_matching_conceptset_id = self.validate_concept_set(m_ocl)
                if mysql_matching_conceptset_id:
                    self.conceptset_comparison[self.MISSING_IN_OCL].remove(mysql_matching_conceptset_id)
                else:
                    self.conceptset_comparison[self.MISSING_IN_MYSQL].append(m_ocl['id'])
                    if self.verbosity >= 2: print 'Missing concept set in MySQL: %s\n' % m_ocl
            else:
                mysql_matching_refmap_id = self.validate_reference_map(m_ocl)
                if mysql_matching_refmap_id:
                    self.refmap_comparison[self.MISSING_IN_OCL].remove(mysql_matching_refmap_id)
                else:
                    self.refmap_comparison[self.MISSING_IN_MYSQL].append(m_ocl['id'])
                    if self.verbosity >= 2: print 'Missing reference map in MySQL: %s\n' % m_ocl

        # Display results of comparison
        print '\n\nMAPPING VALIDATION SUMMARY:'
        print '%s Q/A mapping(s) missing in OCL Export:\n' % len(self.qanda_comparison[self.MISSING_IN_OCL])
        if self.verbosity >= 1: print self.qanda_comparison[self.MISSING_IN_OCL]
        print '\n%s Q/A mapping(s) missing in MySQL:\n' % len(self.qanda_comparison[self.MISSING_IN_MYSQL])
        if self.verbosity >= 1: print self.qanda_comparison[self.MISSING_IN_MYSQL]
        print '\n%s Concept Set(s) mappings missing in OCL Export:\n' % len(self.conceptset_comparison[self.MISSING_IN_OCL])
        if self.verbosity >= 1: print self.conceptset_comparison[self.MISSING_IN_OCL]
        print '\n%s Concept Set(s) mappings missing in MySQL:\n' % len(self.conceptset_comparison[self.MISSING_IN_MYSQL])
        if self.verbosity >= 1: print self.conceptset_comparison[self.MISSING_IN_MYSQL]
        print '\n%s Reference Map(s) missing in OCL Export:\n' % len(self.refmap_comparison[self.MISSING_IN_OCL])
        if self.verbosity >= 1: print self.refmap_comparison[self.MISSING_IN_OCL]
        print '\n%s Reference Map(s) missing in MySQL:\n' % len(self.refmap_comparison[self.MISSING_IN_MYSQL])
        if self.verbosity >= 1: print self.refmap_comparison[self.MISSING_IN_MYSQL]

    def validate_reference_map(self, m_ocl):
        map_type = m_ocl['map_type']
        from_concept_id = m_ocl['from_concept_code']
        to_concept_code = m_ocl['to_concept_code']
        to_source_name = OclOpenmrsHelper.get_omrs_source_id_from_ocl_id(m_ocl['to_source_name'])
        try:
            m_omrs = ConceptReferenceMap.objects.get(map_type__name=map_type,
                                                     concept_reference_term__code=to_concept_code,
                                                     concept_id=from_concept_id,
                                                     concept_reference_term__concept_source__name=to_source_name)
            return m_omrs.concept_map_id
        except ConceptReferenceMap.DoesNotExist:
            return False
        except ConceptReferenceMap.MultipleObjectsReturned:
            print 'Multiple objects returned from MySQL for reference mapping: %s\n' % m_ocl
            return False

    def validate_qanda(self, m_ocl):
        question_concept_id = m_ocl['from_concept_code']
        answer_concept_id = m_ocl['to_concept_code']
        try:
            qa_omrs = ConceptAnswer.objects.get(question_concept_id=question_concept_id,
                                                answer_concept_id=answer_concept_id)
            return qa_omrs.concept_answer_id
        except ConceptAnswer.DoesNotExist:
            return False
        except ConceptAnswer.MultipleObjectsReturned:
            print 'Multiple objects returned for qanda: %s\n' % m_ocl
            return False

    def validate_concept_set(self, m_ocl):
        set_owner_id = m_ocl['from_concept_code']
        set_member_id = m_ocl['to_concept_code']
        try:
            cs_omrs = ConceptSet.objects.get(concept_set_owner_id=set_owner_id,
                                             concept_id=set_member_id)
            return cs_omrs.concept_set_id
        except ConceptSet.DoesNotExist:
            return False
        except ConceptSet.MultipleObjectsReturned:
            print 'Multiple objects returned for concept set: %s\n' % m_ocl
            return False
