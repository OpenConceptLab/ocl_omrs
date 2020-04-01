# ocl_omrs

This django project has scripts that make it easier to work with OCL and OpenMRS:
* **extract_db** will generate a JSON file from an OpenMRS v1.11 concept dictionary formatted for import into OCL
* **import** submits a file for bulk import into OCL
* **validate_export** validates an OCL export file against an OpenMRS v1.11 concept dictionary

## extract_db: OpenMRS Database JSON Export
The extract_db script reads an OpenMRS v1.11 database and extracts the concept and mapping data as JSON formatted for import into OCL. This script is typically run on a local machine with MySQL installed.

1. Update settings.py with MySQL database settings for target OpenMRS concept dictionary

2. Check sources in specified OCL environment:

    python manage.py extract_db --check_sources --env=demo --token=[my-token-here]

3. Check sources and output as OCL-formatted bulk JSON:

    python manage.py extract_db --check_sources --env=demo --token=<my-token-here> --org_id=MyOrg --source_id=MySource --raw -v0 --concepts --mappings --format=bulk > my_ocl_bulk_import_file.json

4. Alternatively, create "old-style" OCL import scripts (separate for concept and mappings)
    designed to be run directly on OCL server:

    python manage.py extract_db --org_id=MyOrg --source_id=MySource --raw -v0 --concepts > concepts.json
    python manage.py extract_db --org_id=MyOrg --source_id=MySource --raw -v0 --mappings > mappings.json

    The 'raw' option indicates that JSON should be formatted one record per line (JSON lines file)
    instead of human-readable format.

Optionally restrict output to a single concept or a limited number of concepts with the `concept_id` or `concept_limit` paramters:
```
# This will extract one Concept with ID 5839
./manage.py extract_db --concept_id 5839

# This will extract the first 10 entries:
./manage.py extract_db --concept_limit 10
```


## validate_export: OCL Export Validation
This command compares OCL export files to an OpenMRS concept dictionary stored in MySql.
Usage:
```
./manage.py validate_export --export=EXPORT_FILE_NAME [--ignore_retired_mappings] [-v[2]]
```


## Design Notes
* OCL-OpenMRS Subscription Module does not handle the OpenMRS drug table, so it is ignored for now
* `models.py` was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet, as not all are used by the OCL-OpenMRS Subscription Module.
