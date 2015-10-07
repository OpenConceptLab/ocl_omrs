# ocl_omrs

This django project has scripts that make it easier to work with OCL and OpenMRS:
* **extract_db** generates JSON files from an OpenMRS v1.11 concept dictionary formatted for import into OCL
* **validate_export** validates an OCL export file against an OpenMRS v1.11 concept dictionary

## validate_export: OCL Export Validation

Before running this, you must set the MySQL database settings in `omrs/settings.py`.

Usage:
```
./manage.py validate_export --export=EXPORT_FILE_NAME [--ignore_retired_mappings] [-v[2]]
```

## extract_db: OpenMRS Database JSON Export

This django project reads a OpenMRS database and extract the concept
data for OCL. Typically you run this on a local machine with MySQL installed.

See the [OpenMRS Website/wiki](https://wiki.openmrs.org/display/docs/Concept+Data+Model) for download of the raw SQL and
data dictionary.

## Configuration

Use this tool in a local environment after setting and loading the OpenMRS SQL file into a MySQL database.

Make sure the settings.py file has the correct database settings.

Run the extract_db management command to extract concepts from the database:

```
    # This will extract one Concept with ID 5839
    ./manage.py extract_db --concept_id 5839

    # This will extract the first 10 entries:
    ./manage.py extract_db --count 10

    # This will extract all concepts
    ./manage.py extract_db

    # normally run this to do full export, output to stdout:

    ./manage.py extract_db --raw


    # In addition if you need to create inputs to mapping import,
    # use the --mapping argument, the mapping data will always
    # write to a file called mapping.txt
    
    ./manage.py extract_db --mapping
```

## Design Notes

The `models.py` file was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet.
