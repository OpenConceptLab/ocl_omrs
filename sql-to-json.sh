#!/usr/bin/env bash
#
# sql-to-json.sh
# Usage: ./sql-to-json.sh local/SQL_FILE OCL_ORG SOURCE_ID [qa|staging|production|demo]
#
# Where:
#  SQL_FILE = name of OpenMRS sql file
#  OCL_ORG = organization ID within OCL (default 'CIEL')
#  SOURCE_ID = name of source within organization (default 'CIEL')
#  OCL_ENV = demo, staging, or production (default 'staging')
#  If FORCE_OLD_MODE=1 in environment, then output will be separate mapping & concepts
# 
# Loads the OpenMRS sql file into a database and then exports it to JSON

SQL_FILE="${1:-openmrs.sql.zip}"
OCL_ORG="${2:-CIEL}"
SOURCE_ID="${3:-CIEL}"
OCL_ENV="${4:-staging}"
FORCE_OLD_MODE="$FORCE_OLD_MODE"

if [ -z "$SQL_FILE" ]
then
  echo "OpenMRS SQL file is required"
  echo "Usage: $0 SQL_FILE [production|staging|demo|qa]"
  exit 1
fi

while true; do
	if [ "$(docker ps -a -f status=exited | grep python)" ]; then

		# Shut down stack
		docker-compose down -v

		# Return program flow to the `wait` line
		break
	else
		# Check status every second
		sleep 1
	fi
done & # Run in the background
BACKGROUND_PID=$!

echo "Processing $SQL_FILE for $OCL_ENV"

# Start up our database

# SQL_FILE="$SQL_FILE" OCL_ORG="$OCL_ORG" SOURCE_ID="$SOURCE_ID" OCL_ENV="$OCL_ENV" FORCE_OLD_MODE="$FORCE_OLD_MODE"
export SQL_FILE
export OCL_ORG
export SOURCE_ID
export OCL_ENV
export FORCE_OLD_MODE
docker-compose up -d

docker-compose logs -f python &

wait $BACKGROUND_PID # Wait for the `while true` loop to be broken

echo "Done."

exit 0