#!/usr/bin/env bash
#
# ciel-to-json.sh
# Usage: ./ciel-to-json.sh local/CIEL_FILE [qa|staging|production|demo]
#
# Where:
#  CIEL_FILE = name of CIEL sql file
#  OCL_ENV = demo, staging, or production
# 
# Loads the CIEL sql file into a database and then exports it to JSON

CIEL_FILE=${1:-ciel.sql.zip}
OCL_ENV=${2:-'staging'}

if [ -z "$CIEL_FILE" ]
then
  echo "CIEL file is required"
  echo "Usage: $0 CIEL_FILE [production|staging|demo|qa]"
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

echo "Processing $CIEL_FILE for $OCL_ENV"

# Start up our database
CIEL_FILE=$CIEL_FILE OCL_ENV=$OCL_ENV docker-compose up -d

docker-compose logs -f python &

wait # Wait for the `while true` loop to be broken

echo "Done."

exit 0