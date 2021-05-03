# ocl_omrs

Generate OCL-formatted bulk import script from a mysql dump of an OpenMRS v1.11 concept dictionary and to validate its
map sources against the OCL staging server (staging.openconceptlab.org):

```
./ciel-to-json.sh local/openmrs_concepts_1.11.4_20200822.sql staging
```

Or, to generate separate JSON files for concepts and mappings (designed to be imported directly on the server):

```
FORCE_OLD_MODE=1 ./ciel-to-json.sh local/openmrs_concepts_1.11.4_20200822.sql staging
```

This django project has scripts that make it easier to work with OCL and OpenMRS:

- **extract_db** will generate a JSON file from an OpenMRS v1.11 concept dictionary formatted for import into OCL
- **import** submits a file for bulk import into OCL
- **validate_export** validates an OCL export file against an OpenMRS v1.11 concept dictionary

## extract_db: OpenMRS Database JSON Export

The extract_db script reads an OpenMRS v1.11 database and extracts the concept and mapping data as JSON formatted for import into OCL. This script is typically run on a local machine with MySQL installed.

1. Import into local mysql
   NOTE: Be sure to use the correct character set for your MySql database. For example, for utf8 use this:

```
CREATE DATABASE ciel_20200706 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
```

NOTE: Load an export into an existing MySql database like this:

```
mysql -u root -p ciel_20200124 < openmrs_concepts_1.11.4_20200124.sql
```

2. Update settings.py with your database settings, including the database (eg ciel_20200706),
   database drivers, username, host, port, and password. name You will see a DATABASES constant
   that looks something like this:

```
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
```

3. Verify that all of the OpenMRS dictionary's external mapping sources are defined in this code
   repository's SOURCE_DIRECTORY (see `/omrs/management/commands/__init__.py`) and exist in specified
   OCL environment:

```
python manage.py extract_db --check_sources --env=demo --token=<my-token-here>
```

The SOURCE_DIRECTORY simply maps an OpenMRS external map source ID ('omrs_id') to a specific source
in OCL. In OCL, a source is identified by an 'ocl_id' (eg ICD-10-WHO), an 'owner_id' (eg 'WHO') and
an 'owner_type' (eg 'org' or 'user'). For example:

```
{'omrs_id':'ICD-10-WHO', 'owner_type':'org', 'owner_id':'WHO', 'ocl_id':'ICD-10-WHO'}
```

The SOURCE_DIRECTORY is unique to each OpenMRS dictionary, however in practice they are often
similar across OpenMRS dictionaries because many of them share CIEL as a common ancestor.
If a source is missing in the SOURCE_DIRECTORY, simply update or add a source mapping to reflect
the missing omrs_id.

If a source is missing in OCL, you may either add that source directly or contact an OCL
administrator.

4. Update the MySql database model (`/omrs/models.py`) to reflect the version of the OpenMRS
   dictionary you are importing. For example, in OpenMRS Platform v2.2, the 'precise' field for
   numeric fields was renamed to 'allow_decimal'. We recommend simply commenting out fields that
   are not applicable to your OpenMRS version.

5. Output as OCL-formatted bulk import JSON:
   (Note: the import file generated is not specific to an environment)

```
python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --concepts --mappings --format=bulk > my_ocl_bulk_import_file.json
```

5. Alternatively, create "old-style" OCL import scripts (separate for concept and mappings)
   designed to be run directly on OCL server:

```
python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --concepts > concepts.json
python manage.py extract_db --org_id=MyOrg --source_id=MySource -v0 --mappings > mappings.json
```

Optionally restrict output to a single concept or a limited number of concepts with the `concept_id` or `concept_limit` paramters. For example, `--concept_id=5839` will only return the concept with an ID of 5839, or `--concept_limit=10` will only return the first 10 concept entries.

## Submit import using bulk import API

If using the bulk import API format (see step #3 above), then you can validate and submit your import file using the following commands:

1. Validate import file:

```
    python manage.py import --validate-only --filename=[filename-here]
```

2. Submit using bulk import API:

```
    python manage.py import --env=production --token=[my-token-here] --filename=[filename-here]
```

## validate_export: OCL Export Validation

This command compares OCL export files to an OpenMRS concept dictionary stored in MySql.
Usage:

```
python manage.py validate_export --export=EXPORT_FILE_NAME [--ignore_retired_mappings] [-v[2]]
```

## Design Notes

- OCL-OpenMRS Subscription Module does not handle the OpenMRS drug table, so it is ignored for now
- `models.py` was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet, as not all are used by the OCL-OpenMRS Subscription Module.
