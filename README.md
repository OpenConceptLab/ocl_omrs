# ocl_omrs

This project has simple Django commands to work with OCL and OpenMRS:
* `extract_db` - Generates a JSON file from an OpenMRS v1.11 concept dictionary formatted for import into OCL
* `import` - Validates and submits a file for bulk import into OCL
* `validate_export` - Validates an OCL export of an OpenMRS-compatible repository against an OpenMRS v1.11 concept dictionary

## extract_db: OpenMRS Database JSON Export
The `extract_db` script extracts the concepts and mappings from an OpenMRS v1.11 database as JSON formatted for import into OCL. This script is typically run on a local machine with MySQL installed. Note that these scripts do not handle the OpenMRS drug table.

1. Update `settings.py` with settings for your MySQL database loaded with an OpenMRS v1.11 concept dictionary.
   If you are trying to import a new CIEL dictionary, you can import it into MySQL like this:
```
    mysql -u root -p ciel_20200124 < openmrs_concepts_1.11.4_20200124.sql
```
2. Verify that the reference sources in the OpenMRS concept dictionary are defined in the SOURCE_DIRECTORY and exist on the target OCL environment:
```
python manage.py extract_db --check_sources --env=demo --token=[my-token-here]
```
    * Add missing reference source definitions directly to the SOURCE_DIRECTORY: https://github.com/OpenConceptLab/ocl_omrs/blob/master/omrs/management/commands/__init__.py#L24
    * Add missing Organizations and Sources to the target OCL environment

3. Output the OpenMRS concept dictionary as OCL-formatted bulk import JSON:
   (Note: the import file generated is not specific to an environment)
```
    python manage.py extract_db --check_sources --env=demo --token=<my-token-here> --org_id=MyOrg --source_id=MySource --raw -v0 --concepts --mappings --format=bulk > my_ocl_bulk_import_file.json
```
4. Alternatively, create "old-style" OCL import scripts designed to be run directly on OCL server. Note that this method requires separate files for concept and mappings.
```
python manage.py extract_db --org_id=MyOrg --source_id=MySource --raw -v0 --concepts > concepts.json
python manage.py extract_db --org_id=MyOrg --source_id=MySource --raw -v0 --mappings > mappings.json
```

Parameters:
* `--raw` - Indicates that resources should be exported one JSON document per line (ie a JSON lines file) instead of in human-readable format.
* `--concept_id` - Restrict output to a single concept ID. For example, `--concept_id=5839` will only export the concept with an ID of 5839.
* `--concept_limit` - Restrict output to the first `n` concepts. For example,  `--concept_limit=10` will only return the first 10 concept entries.

## Validate and submit import using bulk import API
If using the bulk import API format (see step #3 above), then you can validate and submit your import file using the following commands:

1. Validate import file (Note that only limited validation is supported currently):
```
    python manage.py import --validate-only --filename=[filename-here]
```
2. Submit using the OCL bulk import API:
``` 
    python manage.py import --env=production --token=[my-token-here] --filename=[filename-here]
```

## validate_export: OCL Export Validation
This command compares an OCL export of an OpenMRS-compatible repository against an OpenMRS v1.11 concept dictionary. After you use the above scripts to import an OpenMRS concept dictionary into OCL, it is recommended that you download an export of that dictionary from OCL and validate it against the original OpenMRS concept dictionary stored in your local MySQL instance.

* This command compares an OCL export file to an OpenMRS concept dictionary stored in MySql.
Usage:
```
python manage.py validate_export --export=EXPORT_FILE_NAME [--ignore_retired_mappings] [-v[2]]
```

## Design Notes
* `models.py` was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet, as not all are used by these scripts.
