import mysql.connector
import time
import sys
import re
import os
from subprocess import Popen, PIPE

DATABASE_NAME = 'openmrs'

db = None
num_attempts = 0
while True:
    try:
        num_attempts += 1
        db = mysql.connector.connect(
            host="db", user="root", password="openmrs")
        break
    except:
        if num_attempts > 10:
            print("Unable to connect to database")
            sys.exit(1)
        time.sleep(1)

cursor = db.cursor()
print("Creating database")
cursor.execute("CREATE DATABASE %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)

filename = os.environ.get("SQL_FILE") + '.sql'

print("Processing file %s" % filename)
source_file = os.path.abspath(filename)
os.system("mysql -u %s -p%s -h db %s < %s" %
          ("root", "openmrs", "openmrs", source_file))


db.commit()

cursor.close()
db.close()

print("Import complete")
