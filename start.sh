#!/bin/bash
set -e

if [ ${CIEL_FILE: -4} == ".zip" ]
then
  echo "Unzipping file..."
  # Unzip into local subdirectory, ignoring __MACOSX folder
  unzip -o $CIEL_FILE -x __*/* -d local/
  CIEL_FILE=${CIEL_FILE%.*}
fi

# Strip .sql extension
if [ ${CIEL_FILE: -4} == ".sql" ]
then
  CIEL_FILE=${CIEL_FILE%.*}
fi

echo "Importing data..."
python import_ciel.py 

echo "Checking sources..."
python manage.py extract_db --check_sources --env=$OCL_ENV

echo "Exporting to json file..."
python manage.py extract_db --org_id=CIEL --source_id=CIEL -v0 --concepts --mappings --format=bulk > ${CIEL_FILE:-ciel}.json