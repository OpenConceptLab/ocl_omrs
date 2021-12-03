#!/bin/bash
set -e

if [ ${SQL_FILE: -4} == ".zip" ]
then
  echo "Unzipping file..."
  # Unzip into local subdirectory, ignoring __MACOSX folder
  unzip -o $SQL_FILE -x __*/* -d local/
  SQL_FILE=${SQL_FILE%.*}
fi

# Strip .sql extension
if [ ${SQL_FILE: -4} == ".sql" ]
then
  SQL_FILE=${SQL_FILE%.*}
fi

# Wait for database to be ready
./wait-for-it.sh db:3306 -t 30

echo "Importing data..."
python import_sql.py 

echo "Checking sources..."
python manage.py extract_db --check_sources --env=$OCL_ENV

if [ "$FORCE_OLD_MODE" = 1 ]
then
  echo "Exporting old style json files..."
  python manage.py extract_db --org_id=${OCL_ORG} --source_id=${SOURCE_ID} -v0 --concepts --use_gold_mappings=${USE_GOLD_MAPPINGS:-0} > ${SQL_FILE:-openmrs}-concepts.json
  python manage.py extract_db --org_id=${OCL_ORG} --source_id=${SOURCE_ID} -v0 --mappings --use_gold_mappings=${USE_GOLD_MAPPINGS:-0} > ${SQL_FILE:-openmrs}-mappings.json
else
  echo "Exporting ${OCL_ORG} to json file..."
  python manage.py extract_db --org_id=${OCL_ORG} --source_id=${SOURCE_ID} -v0 --concepts --mappings --format=bulk --use_gold_mappings=${USE_GOLD_MAPPINGS:-0} > ${SQL_FILE:-openmrs}.json
fi
