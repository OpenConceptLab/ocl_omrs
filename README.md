# ocl_omrs

This django project has scripts that make it easier to work with OCL and OpenMRS:
* **extract_db** generates JSON files from an OpenMRS v1.11 concept dictionary formatted for import into OCL
* **validate_export** validates an OCL export file against an OpenMRS v1.11 concept dictionary

Before running any of these commands, you must first set the MySQL database settings in `omrs/settings.py`.


## validate_export: OCL Export Validation

This command compares OCL export files to an OpenMRS concept dictionary stored in MySql.

Usage:
```
./manage.py validate_export --export=EXPORT_FILE_NAME [--ignore_retired_mappings] [-v[2]]
```


## extract_db: OpenMRS Database JSON Export

This command produces OCL JSON import files for concepts and mappings stored in an OpenMRS v1.11 concept dictionary saved in MySql. Typically you run this on a local machine with MySQL installed.

See the [OpenMRS Website/wiki](https://wiki.openmrs.org/display/docs/Concept+Data+Model) for download of the raw SQL and
data dictionary.

Separate files should be created for concepts and mappings, for example:

    manage.py extract_db --org_id=CIEL --source_id=CIEL --raw -v0 --concepts > concepts.json
    manage.py extract_db --org_id=CIEL --source_id=CIEL --raw -v0 --mappings > mappings.json

By default JSON is outputted in a human-readable format. Use the `raw` option to indicate that JSON should be formatted one record per line (JSON lines file), which is the required format for OCL import files.

Set verbosity to 0 (e.g. `-v0`) to suppress the results summary output, which is required for the OCL import files. Set verbosity to 3 (`-v3`) to see all debug output.

To create a smaller test dataset, use the `concept_limit` option (e.g. `--concept_limit=2000`):

    manage.py extract_db --org_id=CIEL --source_id=CIEL --raw -v0 --concept_limit=2000 --concepts > c2k.json
    manage.py extract_db --org_id=CIEL --source_id=CIEL --raw -v0 --concept_limit=2000 --mappings > m2k.json

Note that the `concept_limit` parameter simply sets a maximum value for the OpenMRS concept_id. It is not a count of concepts, which means it current only works well for sequential numeric ID systems.

You should validate reference sources before generating the export with the `check_sources` option:

    manage.py extract_db --check_sources --env=... --token=...

It is also possible to create a list of retired concept IDs (this is not used during import):

    manage.py extract_db --org_id=CIEL --source_id=CIEL --raw -v0 --retired > retired_concepts.json


NOTES:
- OCL does not handle the OpenMRS drug table -- it is ignored for now


## Design Notes

The `models.py` file was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet, as not all are imported into OCL.
