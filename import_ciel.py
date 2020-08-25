import mysql.connector
import time
import sys
import re
import os

DATABASE_NAME = 'ciel'

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


def execute_sql(sql):
    try:
        cursor.execute(sql)
    except Exception as e:
        # When importing CIEL to an empty db, we can ignore missing global_property references
        if "global_property" in str(e):
            pass
        else:
            print("Error executing sql '%s'. Detail: %s" %
                  (sql.strip(), str(e)))


filename = os.environ.get("CIEL_FILE") + '.sql'
print("Processing file %s" % filename)
file = open(filename, 'r')
sql = ""
in_multiline_comment = False
for line in file:
    if not in_multiline_comment and re.search(r"^\s*/\*", line):
        # If we discover multiline comment, execute any remaining sql and stop executing until
        # comment ends. We only handle multiline comments on separate lines from actual sql.
        if sql:
            execute_sql(sql)
            sql = ""
        if not re.search(r"\*/", line):
            in_multiline_comment = True
        continue
    if in_multiline_comment and re.search(r"\*/", line):
        # End of multiline comment
        in_multiline_comment = False
        continue
    if in_multiline_comment:
        # Ignore text within multiline comments
        continue
    if re.search(r";\s*(--.*)?", line):
        # Line ends with semicolon, so we execute what we've got queued
        sql += line
        execute_sql(sql)
        sql = ""
        continue
    if re.search(r"^\s*--", line):
        # Ignore single line comments
        continue
    if not line.strip():
        # Ignore blank lines
        continue
    sql += line

db.commit()

cursor.close()
db.close()
print("Import complete")
