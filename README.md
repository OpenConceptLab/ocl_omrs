# OpenMRS Database Extract/Export

This django project reads a OpenMRS database and extract the concept
data for OCL.

See the [OpenMRS Website/wiki](https://wiki.openmrs.org/display/docs/Concept+Data+Model) for download of the raw SQL and
data dictionary.

# Configuration

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

```

## Design Notes

The `models.py1 file was created partially by scanning the mySQL schema, and the fixed up by hand. Not all classes are fully mapped yet.
