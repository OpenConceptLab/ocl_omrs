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

# Wait for database to be ready
./wait-for-it.sh db:3306 --timeout 30

echo "Importing data..."
python import_ciel.py 

echo "Checking sources..."
python manage.py extract_db --check_sources --env=$OCL_ENV

if [ "$FORCE_OLD_MODE" = 1 ]
then
  echo "Exporting old style json files..."
  python manage.py extract_db --org_id=CIEL --source_id=CIEL -v0 --concepts > ${CIEL_FILE:-ciel}-concepts.json
  python manage.py extract_db --org_id=CIEL --source_id=CIEL -v0 --mappings > ${CIEL_FILE:-ciel}-mappings.json
else
  echo "Exporting to json file..."
  python manage.py extract_db --org_id=CIEL --source_id=CIEL -v0 --concepts --mappings --format=bulk > ${CIEL_FILE:-ciel}.json
fi
