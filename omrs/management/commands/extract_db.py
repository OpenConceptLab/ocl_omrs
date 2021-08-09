"""
Commands to create JSON for importing OpenMRS v1.11 concept dictionary into OCL.

1. Import into local mysql
   NOTE: Be sure to use the correct character set for your MySql database, ex:

    CREATE DATABASE ciel_20200706 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

2. Update settings.py with your database settings, including the database (eg ciel_20200706),
   database drivers, username, host, port, and password. name You will see a DATABASES constant
   that looks something like this:

    DATABASES = {
        'default': {
            'NAME': 'ciel_20200706',
            'ENGINE': 'django.db.backends.mysql',
            'USER': 'root',
            'HOST': 'localhost',
            'PORT': '3307',
            'PASSWORD': 'my-password',
        }
    }

3. Verify that all of the OpenMRS dictionary's external mapping sources are defined in this code
   repository's SOURCE_DIRECTORY (see /omrs/management/commands/__init__.py) and exist in specified
   OCL environment:

        python manage.py extract_db --check_sources --env=demo --token=<my-token-here>

   The SOURCE_DIRECTORY simply maps an OpenMRS external map source ID ('omrs_id') to a specific source
   in OCL. In OCL, a source is identified by an 'ocl_id' (eg ICD-10-WHO), an 'owner_id' (eg 'WHO') and
   an 'owner_type' (eg 'org' or 'user'). For example:

        {'omrs_id':'ICD-10-WHO', 'owner_type':'org', 'owner_id':'WHO', 'ocl_id':'ICD-10-WHO'}

   The SOURCE_DIRECTORY is unique to each OpenMRS dictionary, however in practice they are often
   similar across OpenMRS dictionaries because many of them share CIEL as a common ancestor.
   If a source is missing in the SOURCE_DIRECTORY, simply update or add a source mapping to reflect
   the missing omrs_id.

   If a source is missing in OCL, you may either add that source directly or contact an OCL
   administrator.

4. Update the MySql database model (/omrs/models.py) to reflect the version of the OpenMRS
   dictionary you are importing. For example, Platform 2.2 (TRUNK-5333) renamed the 'precise'
   field for numeric fields to 'allow_decimal'. We recommend simply commenting out fields
   that are not applicable to your OpenMRS version or, for TRUNK-5333 renaming the 'precise'
   attribute of the concept_numeric table to 'allow_decimal' within the SQL being imported.

5. Output as OCL-formatted bulk import JSON:

    python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --concepts --mappings
        --format=bulk > my_ocl_bulk_import_file.json

6. Alternatively, create "old-style" OCL import scripts (separate for concept and mappings)
    designed to be run directly on OCL server:

    python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --concepts > concepts.json
    python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --mappings > mappings.json

NOTES:
- OCL does not handle the OpenMRS drug table -- it is ignored for now

"""
from optparse import make_option
import requests
import json
from django.core.management import BaseCommand, CommandError
from omrs.models import Concept, ConceptReferenceSource
from omrs.management.commands import OclOpenmrsHelper, UnrecognizedSourceException
import ocldev.oclresourcelist
import urllib


class Command(BaseCommand):
    """ Extract concepts from OpenMRS database in the form of json """

    OCL_IMPORT_FILE_FORMAT_STANDARD = 'standard'
    OCL_IMPORT_FILE_FORMAT_BULK = 'bulk'
    OCL_IMPORT_FILE_FORMATS = [
        OCL_IMPORT_FILE_FORMAT_STANDARD, OCL_IMPORT_FILE_FORMAT_BULK]

    # Command attributes
    help = 'Extract concepts from OpenMRS database in the form of json'
    option_list = BaseCommand.option_list + (
        make_option('--concept_id',
                    action='store',
                    dest='concept_id',
                    default=None,
                    help='ID for concept to export, if specified only export this one. e.g. 5839'),
        make_option('--concept_limit',
                    action='store',
                    dest='concept_limit',
                    default=None,
                    help='Use to limit the number of concepts exported. Useful for testing.'),
        make_option('--mappings',
                    action='store_true',
                    dest='mapping',
                    default=False,
                    help='Create mapping input file.'),
        make_option('--concepts',
                    action='store_true',
                    dest='concept',
                    default=False,
                    help='Create concept input file.'),
        make_option('--indent',
                    action='store',
                    dest='indent',
                    default=None,
                    help='Indent JSON output for human-readability; default is 0.'),
        make_option('--org_id',
                    action='store',
                    dest='org_id',
                    default='',
                    help='org_id that owns the dictionary being imported (e.g. CIEL)'),
        make_option('--source_id',
                    action='store',
                    dest='source_id',
                    default='',
                    help='source_id of dictionary being imported (e.g. ICD-10-WHO)'),
        make_option('--check_sources',
                    action='store_true',
                    dest='check_sources',
                    default=False,
                    help='Validates that all reference sources in OpenMRS have been defined in OCL.'),
        make_option('--format',
                    action='store',
                    dest='ocl_import_file_format',
                    default=OCL_IMPORT_FILE_FORMAT_STANDARD,
                    help='JSON export format, "standard" (default) or "bulk"'),
        make_option('--env',
                    action='store',
                    dest='ocl_api_env',
                    default='',
                    help='Set the target for reference source validation to "dev", "staging", "demo", or "production"'),
        make_option('--token',
                    action='store',
                    dest='token',
                    default='',
                    help='OCL API token to validate OpenMRS reference sources'),
    )

    def handle(self, *args, **options):
        """
        This method is called first directly from the command line, handles options, and calls
        export() depending on options set.
        """

        # Handle command line arguments
        self.org_id = options['org_id']
        self.source_id = options['source_id']
        self.concept_id = options['concept_id']
        self.concept_limit = options['concept_limit']
        self.indent = options['indent']
        self.do_mapping = options['mapping']
        self.do_concept = options['concept']
        if self.concept_limit is not None:
            self.concept_limit = int(self.concept_limit)
        self.verbosity = int(options['verbosity'])
        self.ocl_api_token = options['token']
        self.ocl_api_env = ''
        if options['ocl_api_env']:
            self.ocl_api_env = options['ocl_api_env'].lower()
        self.ocl_import_file_format = options['ocl_import_file_format']

        # Option debug output
        if self.verbosity >= 2:
            print 'COMMAND LINE OPTIONS:', options

        # Validate the options
        self.validate_options()

        # Validate reference sources
        if options['check_sources']:
            if self.verbosity:
                print 'CHECKING REFERENCE SOURCES ON "%s"...' % self.ocl_api_env
            if not self.check_sources():
                print '\nERROR: Missing required reference sources. Please correct and try again.'
                exit(1)

        # Initialize counters
        self.cnt_total_concepts_processed = 0
        self.cnt_concepts_exported = 0
        self.cnt_internal_mappings_exported = 0
        self.cnt_external_mappings_exported = 0
        self.cnt_ignored_self_mappings = 0
        self.cnt_questions_exported = 0
        self.cnt_answers_exported = 0
        self.cnt_concept_sets_exported = 0
        self.cnt_set_members_exported = 0
        self.cnt_retired_concepts_exported = 0

        # Process concepts and mappings script
        if self.do_mapping or self.do_concept:
            self.export()
            if self.verbosity:
                self.print_export_summary()

    def validate_options(self):
        """
        Returns true if command line options are valid. Prints error message if invalid.
        """
        # If concept/mapping export enabled, org/source IDs are required & must be valid mnemonics
        # TODO: Check that org and source IDs are valid mnemonics
        # TODO: Check that specified org and source IDs exist in OCL
        if (self.do_mapping or self.do_concept) and (not self.org_id or not self.source_id):
            raise CommandError(
                ("ERROR: 'org_id' and 'source_id' are required options for a concept or "
                 "mapping export and must be valid identifiers for an organization and "
                 "source in OCL"))
        if self.ocl_api_env and self.ocl_api_env not in OclOpenmrsHelper.OCL_API_URL:
            raise CommandError(
                'Invalid "env" option provided: %s' % self.ocl_api_env)
        if self.ocl_import_file_format not in self.OCL_IMPORT_FILE_FORMATS:
            raise CommandError(
                'Invalid "format" option provided: %s' % self.ocl_import_file_format)
        return True

    def print_export_summary(self):
        """ Outputs a summary of the results """
        print '------------------------------------------------------'
        print 'SUMMARY'
        print '------------------------------------------------------'
        print 'Total concepts processed: %d' % self.cnt_total_concepts_processed
        if self.do_concept:
            print 'EXPORT COUNT: Concepts: %d' % self.cnt_concepts_exported
        if self.do_mapping:
            print 'EXPORT COUNT: All Mappings: %d' % (self.cnt_internal_mappings_exported +
                                                      self.cnt_external_mappings_exported +
                                                      self.cnt_answers_exported +
                                                      self.cnt_set_members_exported)
            print 'EXPORT COUNT: Internal Mappings: %d' % self.cnt_internal_mappings_exported
            print 'EXPORT COUNT: External Mappings: %d' % self.cnt_external_mappings_exported
            print 'EXPORT COUNT: Linked Answer Mappings: %d' % self.cnt_answers_exported
            print 'EXPORT COUNT: Set Member Mappings: %d' % self.cnt_concepts_exported
            print 'Questions Processed: %d' % self.cnt_questions_exported
            print 'Concept Sets Processed: %d' % self.cnt_concept_sets_exported
            print 'Ignored Self Mappings: %d' % self.cnt_ignored_self_mappings
        print '------------------------------------------------------'

    def check_sources(self):
        """ Validates that all reference sources in OpenMRS have been defined in OCL. """

        # Set things up
        ocl_env_url = '%s/' % OclOpenmrsHelper.OCL_API_URL[self.ocl_api_env]
        headers = {}
        if self.ocl_api_token:
            headers['Authorization'] = 'Token %s' % self.ocl_api_token

        # Grab the list of references sources in the OpenMRS dictionary from MySql
        reference_sources = ConceptReferenceSource.objects.all()
        reference_sources = reference_sources.filter(retired=0)
        enum_reference_sources = enumerate(reference_sources)

        # Check if each reference source exists in the specified OCL environment
        matching_sources = []
        missing_source_in_ocl = []
        missing_source_definition = []
        org_fields_to_remove = ['collections_url', 'members_url', 'uuid', 'public_sources', 'url',
                                'public_collections', 'created_by', 'created_on', 'updated_by', 'members', 'updated_on', 'sources_url']
        source_fields_to_remove = ['versions_url', 'created_on', 'updated_by', 'uuid', 'created_by', 'mappings_url',
                                   'owner_url', 'concepts_url', 'versions', 'active_mappings', 'url', 'active_concepts', 'updated_on']
        for num, source in enum_reference_sources:
            if self.verbosity >= 2:
                print 'Checking OpenMRS Reference source: "%s"' % source.name

            # Check if the source definition exists in local source directory
            try:
                ocl_source_id = OclOpenmrsHelper.get_ocl_source_id_from_omrs_id(
                    source.name)
                ocl_org_id = OclOpenmrsHelper.get_source_owner_id(
                    ocl_source_id=ocl_source_id)
            except UnrecognizedSourceException:
                missing_source_definition.append({
                    'omrs_source': source,
                    'omrs_ref_source_name': source.name
                })
                if self.verbosity >= 2:
                    print '  ...Missing reference source definition'
                continue
            if self.verbosity >= 2:
                print '  ...Corresponding source "%s" and owner "%s" found in source directory' % (
                    ocl_source_id, ocl_org_id)

            # Check that org:source exists in OCL
            ocl_org_url = ocl_env_url + 'orgs/%s/' % (q(ocl_org_id))
            ocl_source_url = ocl_env_url + \
                'orgs/%s/sources/%s/' % (q(ocl_org_id), q(ocl_source_id))
            ocl_org_response = requests.get(ocl_org_url, headers=headers)
            ocl_source_response = requests.get(ocl_source_url, headers=headers)
            if self.verbosity >= 2:
                try:
                    ocl_org_json = ocl_org_response.json()
                    ocl_source_json = ocl_source_response.json()
                    [ocl_org_json.pop(key) for key in org_fields_to_remove]
                    [ocl_source_json.pop(key)
                     for key in source_fields_to_remove]
                    print json.dumps(ocl_org_json)
                    print json.dumps(ocl_source_json)
                except Exception:
                    pass
            current_source = {
                'omrs_source': source,
                'omrs_ref_source_name': source.name,
                'ocl_org_id': ocl_org_id,
                'ocl_source_id': ocl_source_id,
                'ocl_source_url': ocl_source_url,
                'response_code': ocl_source_response.status_code
            }
            if ocl_source_response.status_code != requests.codes.OK:
                missing_source_in_ocl.append(current_source)
                if self.verbosity >= 2:
                    print '  ...Org or source not found in OCL: %s' % ocl_source_url
            else:
                matching_sources.append(current_source)
                if self.verbosity >= 2:
                    print '  ...Org and source found in OCL: %s' % ocl_source_url

        # Display the results
        if self.verbosity:
            print '------------------------------------------------------'
            print 'CHECK SOURCES RESULTS:'
            print '** Matched Sources:', len(matching_sources)
            for source in matching_sources:
                print '%s: %s' % (source['omrs_ref_source_name'], source['ocl_source_url'])

            print '\n** Missing Source Definitions:', len(missing_source_definition)
            for source in missing_source_definition:
                source_definition = {
                    'owner_type': 'org',
                    'omrs_id': source['omrs_ref_source_name'],
                    'owner_id': '',
                    'ocl_id': ''
                }
                print '\n%s:' % source['omrs_ref_source_name']
                print '- OpenMRS Reference Source Definition:', source['omrs_source'].__dict__
                print '- Template to add to source definitions:', json.dumps(source_definition)

            print '\n** Missing Sources in OCL:', len(missing_source_in_ocl)
            for source in missing_source_in_ocl:
                print '\n%s:' % source['omrs_ref_source_name']
                print '- OpenMRS Reference Source Definition:', source['omrs_source'].__dict__
                print '- Source Details:', source

        if missing_source_definition or missing_source_in_ocl:
            return False
        return True

    def export(self):
        """
        Main loop to export all concepts and/or their mappings.
        Loop thru all concepts and mappings and generates JSON export in the OCL format.
        Note that the retired status of concepts is not handled here.
        """

        # Create the concept enumerator, applying 'concept_id' and 'concept_limit' options
        if self.concept_id is not None:
            # If 'concept_id' option set, fetch a single concept and convert to enumerator
            concept = Concept.objects.get(concept_id=self.concept_id)
            concept_enumerator = enumerate([concept])
        else:
            # Fetch all concepts and filter with 'concept_limit' if set
            # TODO: 'concept_limit' is based on numeric value of concept_id not on actual count
            concept_results = Concept.objects.all()
            if self.concept_limit is not None:
                concept_results = concept_results.filter(
                    concept_id__lte=self.concept_limit)
            concept_enumerator = enumerate(concept_results)

        # Iterate concept enumerator and process the export
        resource_list_concepts = ocldev.oclresourcelist.OclJsonResourceList()
        resource_list_mappings = ocldev.oclresourcelist.OclJsonResourceList()
        for num, concept in concept_enumerator:
            self.cnt_total_concepts_processed += 1
            export_data = ''
            if self.do_concept:
                export_data = self.export_concept(concept)
                if export_data:
                    resource_list_concepts.append(export_data)
                    # print json.dumps(export_data, indent=self.indent)
            if self.do_mapping:
                export_data = self.export_all_mappings_for_concept(concept)
                if export_data:
                    resource_list_mappings.append(export_data)
                    # for map_dict in export_data:
                    #     print json.dumps(map_dict, indent=self.indent)

        # Output
        if len(resource_list_concepts):
            for resource in resource_list_concepts:
                print json.dumps(resource, indent=self.indent)
        if len(resource_list_mappings):
            for resource in resource_list_mappings:
                print json.dumps(resource, indent=self.indent)

    def export_concept(self, concept):
        """
        Export one concept as OCL-formatted dictionary.

        :param concept: Concept to export from OpenMRS database.
        :returns: OCL-formatted dictionary for the concept.

        Note:
        - OMRS does not have locale_preferred or description_type metadata, so these are omitted
        """

        # Iterate the concept export counter
        self.cnt_concepts_exported += 1

        # Core concept fields
        extras = {}
        data = {}
        data['id'] = str(concept.concept_id)
        data['concept_class'] = concept.concept_class.name
        data['datatype'] = concept.datatype.name
        data['external_id'] = concept.uuid
        data['retired'] = concept.retired
        if concept.is_set:
            extras['is_set'] = concept.is_set

        # Add type, owner and source fields for bulk import
        if self.ocl_import_file_format == self.OCL_IMPORT_FILE_FORMAT_BULK:
            data['type'] = 'Concept'
            data['owner'] = self.org_id
            data['owner_type'] = 'Organization'
            data['source'] = self.source_id

        # Concept Names
        names = []
        for concept_name in concept.conceptname_set.all():
            if not concept_name.voided:
                names.append({
                    'name': concept_name.name,
                    'name_type': concept_name.concept_name_type if concept_name.concept_name_type else '',
                    'locale': concept_name.locale,
                    'locale_preferred': concept_name.locale_preferred,
                    'external_id': concept_name.uuid,
                })
        data['names'] = names

        # Concept Descriptions
        # NOTE: OMRS does not have description_type or locale_preferred -- omitted for now
        descriptions = []
        for concept_description in concept.conceptdescription_set.all():
            if concept_description.description:
                descriptions.append({
                    'description': concept_description.description,
                    'locale': concept_description.locale,
                    'external_id': concept_description.uuid
                })
        data['descriptions'] = descriptions

        # If the concept is of numeric type, map concept's numeric type data as extras
        for numeric_metadata in concept.conceptnumeric_set.all():
            extras_dict = {}
            add_f(extras_dict, 'hi_absolute', numeric_metadata.hi_absolute)
            add_f(extras_dict, 'hi_critical', numeric_metadata.hi_critical)
            add_f(extras_dict, 'hi_normal', numeric_metadata.hi_normal)
            add_f(extras_dict, 'low_absolute', numeric_metadata.low_absolute)
            add_f(extras_dict, 'low_critical', numeric_metadata.low_critical)
            add_f(extras_dict, 'low_normal', numeric_metadata.low_normal)
            add_f(extras_dict, 'units', numeric_metadata.units)
            add_f(extras_dict, 'allow_decimal', numeric_metadata.allow_decimal)
            add_f(extras_dict, 'display_precision',
                  numeric_metadata.display_precision)
            extras.update(extras_dict)
        data['extras'] = extras

        return data

    def export_all_mappings_for_concept(self, concept, export_qanda=True, export_set_members=True):
        """
        Export mappings for the specified concept, including its set members and linked answers.

        OCL stores all concept relationships as mappings, so OMRS mappings, Q-AND-A and
        CONCEPT-SETS are all handled here and exported as mapping JSON.
        :param concept: Concept with the mappings to export from OpenMRS database.
        :returns: List of OCL-formatted mapping dictionaries for the concept.
        """
        maps = []

        # Import OpenMRS mappings
        new_maps = self.export_concept_mappings(concept)
        if new_maps:
            maps += new_maps

        # Import OpenMRS Q&A
        if export_qanda:
            new_maps = self.export_concept_qanda(concept)
            if new_maps:
                maps += new_maps

        # Import OpenMRS Concept Set Members
        if export_set_members:
            new_maps = self.export_concept_set_members(concept)
            if new_maps:
                maps += new_maps

        return maps

    def export_concept_mappings(self, concept):
        """
        Generate OCL-formatted mappings for the concept, excluding set members and Q/A.

        Creates both internal and external mappings, based on the mapping definition.
        :param concept: Concept with the mappings to export from OpenMRS database.
        :returns: List of OCL-formatted mapping dictionaries for the concept.
        """
        export_data = []
        for ref_map in concept.conceptreferencemap_set.all():
            map_dict = None

            # Internal Mapping
            if ref_map.concept_reference_term.concept_source.name == self.org_id:
                if str(concept.concept_id) == ref_map.concept_reference_term.code:
                    # mapping to self, so ignore
                    self.cnt_ignored_self_mappings += 1
                    continue
                map_dict = self.generate_internal_mapping(
                    map_type=ref_map.map_type.name,
                    from_concept=concept,
                    to_concept_code=ref_map.concept_reference_term.code,
                    external_id=ref_map.concept_reference_term.uuid)
                self.cnt_internal_mappings_exported += 1

            # External Mapping
            else:
                # Prepare to_source_id
                omrs_to_source_id = ref_map.concept_reference_term.concept_source.name
                to_source_id = OclOpenmrsHelper.get_ocl_source_id_from_omrs_id(
                    omrs_to_source_id)
                to_org_id = OclOpenmrsHelper.get_source_owner_id(
                    ocl_source_id=to_source_id)

                # Generate the external mapping dictionary
                map_dict = self.generate_external_mapping(
                    map_type=ref_map.map_type.name,
                    from_concept=concept,
                    to_org_id=to_org_id,
                    to_source_id=to_source_id,
                    to_concept_code=ref_map.concept_reference_term.code,
                    to_concept_name=ref_map.concept_reference_term.name,
                    external_id=ref_map.uuid)

                self.cnt_external_mappings_exported += 1

            if map_dict:
                export_data.append(map_dict)

        return export_data

    def export_concept_qanda(self, concept):
        """
        Generate OCL-formatted mappings for the linked answers in this concept.
        In OpenMRS, linked answers are always internal mappings.
        :param concept: Concept with the linked answers to export from OpenMRS database.
        :returns: List of OCL-formatted mapping dictionaries representing the linked answers.
        """
        if not concept.question_answer.count():
            return []

        # Increment number of concept questions prepared for export
        self.cnt_questions_exported += 1

        # Export each of this concept's linked answers as an internal mapping
        maps = []
        for answer in concept.question_answer.all():
            map_dict = self.generate_internal_mapping(
                map_type=OclOpenmrsHelper.MAP_TYPE_Q_AND_A,
                from_concept=concept,
                to_concept_code=answer.answer_concept.concept_id,
                external_id=answer.uuid)
            maps.append(map_dict)
            self.cnt_answers_exported += 1

        return maps

    def export_concept_set_members(self, concept):
        """
        Generate OCL-formatted mappings for the set members in this concept.
        In OpenMRS, set members are always internal mappings.
        :param concept: Concept with the set members to export from OpenMRS database.
        :returns: List of OCL-formatted mapping dictionaries representing the set members.
        """
        if not concept.conceptset_set.count():
            return []

        # Iterate number of concept sets prepared for export
        self.cnt_concept_sets_exported += 1

        # Export each of this concept's set members as an internal mapping
        maps = []
        for set_member in concept.conceptset_set.all():
            map_dict = self.generate_internal_mapping(
                map_type=OclOpenmrsHelper.MAP_TYPE_CONCEPT_SET,
                from_concept=concept,
                to_concept_code=set_member.concept.concept_id,
                external_id=set_member.uuid)
            maps.append(map_dict)
            self.cnt_set_members_exported += 1

        return maps

    def generate_internal_mapping(self, map_type=None, from_concept=None, to_concept_code=None,
                                  external_id=None, retired=False):
        """ Generate OCL-formatted dictionary for an internal mapping based on passed params. """
        map_dict = {}
        map_dict['map_type'] = map_type
        map_dict['from_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
            q(self.org_id), q(self.source_id), q(from_concept.concept_id))
        map_dict['to_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
            q(self.org_id), q(self.source_id), q(to_concept_code))
        map_dict['retired'] = bool(retired)
        add_f(map_dict, 'external_id', external_id)
        if self.ocl_import_file_format == self.OCL_IMPORT_FILE_FORMAT_BULK:
            map_dict['type'] = 'Mapping'
            map_dict['owner'] = self.org_id
            map_dict['owner_type'] = 'Organization'
            map_dict['source'] = self.source_id
        return map_dict

    def generate_external_mapping(self, map_type=None, from_concept=None,
                                  to_org_id=None, to_source_id=None,
                                  to_concept_code=None, to_concept_name=None,
                                  external_id=None, retired=False):
        """ Generate OCL-formatted dictionary for an external mapping based on passed params. """
        map_dict = {}
        map_dict['map_type'] = map_type
        map_dict['from_concept_url'] = '/orgs/%s/sources/%s/concepts/%s/' % (
            q(self.org_id), q(self.source_id), q(from_concept.concept_id))
        map_dict['to_source_url'] = '/orgs/%s/sources/%s/' % (
            q(to_org_id), q(to_source_id))
        map_dict['to_concept_code'] = to_concept_code
        map_dict['retired'] = bool(retired)
        add_f(map_dict, 'to_concept_name', to_concept_name)
        add_f(map_dict, 'external_id', external_id)
        if self.ocl_import_file_format == self.OCL_IMPORT_FILE_FORMAT_BULK:
            map_dict['type'] = 'Mapping'
            map_dict['owner'] = self.org_id
            map_dict['owner_type'] = 'Organization'
            map_dict['source'] = self.source_id
        return map_dict


# HELPER METHODS

def add_f(dictionary, key, value):
    """Utility function: Adds new field to the dictionary if value is not None"""
    if value is not None:
        dictionary[key] = value


def q(s):
    """Utility function to URL encode value using quote_plus and work if int passed"""
    return urllib.quote_plus(str(s))
