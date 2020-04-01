from optparse import make_option
import json
from django.core.management import BaseCommand, CommandError
from omrs.management.commands import OclOpenmrsHelper
import ocldev.oclvalidator
import ocldev.oclfleximporter


class Command(BaseCommand):
    """ Import and validate an import file """

    help = 'Import and validate an OCL-formatted import file.'
    option_list = BaseCommand.option_list + (
        make_option('--filename',
                    action='store',
                    dest='ocl_import_filename',
                    default=None,
                    help='OCL import filename'),
        make_option('--validate-only',
                    action='store_true',
                    dest='validate_only',
                    default=None,
                    help='Validates the import file without importing'),
        make_option('--env',
                    action='store',
                    dest='ocl_api_env',
                    default=None,
                    help='Set the target for import to "dev", "staging", "demo", or "production"'),
        make_option('--token',
                    action='store',
                    dest='ocl_api_token',
                    default=None,
                    help='OCL API token to validate OpenMRS reference sources'),
    )

    def handle(self, *args, **options):
        """ """

        # Validate command line arguments
        if options['verbosity']:
            print options
        if not options['ocl_import_filename']:
            raise CommandError('Missing required argument "filename"')
        if not options['validate_only']:
            if options['ocl_api_env'] not in OclOpenmrsHelper.OCL_API_URL:
                raise CommandError('Invalid "env" option provided: %s' % options['ocl_api_env'])
            if not options['ocl_api_token']:
                raise CommandError('"token" required to process import. None provided')

        # Load the file -- must be OCL-formatted JSON
        input_list = []
        with open(options['ocl_import_filename']) as json_lines_input_file:
            for raw_json_line in json_lines_input_file:
                input_list.append(json.loads(raw_json_line))
        print '%s resources loaded from \"%s\"' % (len(input_list), options['ocl_import_filename'])

        # Validate resources
        print 'Validating...'
        ocldev.oclvalidator.OclJsonValidator.validate(input_list)

        # Run the import
        if options['validate_only']:
            print 'Skipping import due to settings...'
        else:
            ocl_api_url_root = OclOpenmrsHelper.OCL_API_URL[options['ocl_api_env']]
            print 'Submitting bulk import to "%s"...' % ocl_api_url_root
            import_request = ocldev.oclfleximporter.OclBulkImporter.post(
                file_path=options['ocl_import_filename'],
                api_url_root=ocl_api_url_root,
                api_token=options['ocl_api_token'])
            import_request.raise_for_status()
            import_response = import_request.json()
            task_id = import_response['task']
            print 'Bulk Import Task ID: %s' % task_id
            print 'Request status at: %s/manage/bulkimport/?task=%s' % (ocl_api_url_root, task_id)
