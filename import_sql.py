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


def execute_sql(sql):
    try:
        cursor.execute(sql)
    except Exception as e:
        # When importing OpenMRS to an empty db, we can ignore missing global_property references
        if "global_property" in str(e):
            pass
        else:
            print("Error executing sql '%s'. Detail: %s" %
                  (sql.strip(), str(e)))


filename = os.environ.get("SQL_FILE") + '.sql'

print("Processing file %s" % filename)
source_file = os.path.abspath(filename)
os.system("mysql -u %s -p%s -h db %s < %s" %
          ("root", "openmrs", "ciel", source_file))

# file = open(filename, 'r')
# sql = ""
# in_multiline_comment = False
# for line in file:
#     if not in_multiline_comment and re.search(r"^\s*/\*", line):
#         # If we discover multiline comment, execute any remaining sql and stop executing until
#         # comment ends. We only handle multiline comments on separate lines from actual sql.
#         if sql:
#             print("""sql="%s" """ % sql)  # debug
#             execute_sql(sql)
#             sql = ""
#         if not re.search(r"\*/", line):
#             in_multiline_comment = True
#         continue
#     if in_multiline_comment and re.search(r"\*/", line):
#         # End of multiline comment
#         in_multiline_comment = False
#         continue
#     if in_multiline_comment:
#         # Ignore text within multiline comments
#         continue
#     if re.search(r";\s*(--.*)?", line):
#         # Line ends with semicolon, so we execute what we've got queued
#         sql += line
#         print("""sql="%s" """ % sql)  # debug
#         execute_sql(sql)
#         sql = ""
#         continue
#     if re.search(r"^\s*--", line):
#         # Ignore single line comments
#         continue
#     if not line.strip():
#         # Ignore blank lines
#         continue
#     sql += line

db.commit()

cursor.close()
db.close()

# process = Popen(['mysql', DATABASE_NAME, '-u', 'root', '-p', 'openmrs'],
#                 stdout=PIPE, stdin=PIPE)
# source_file = os.path.abspath(filename)
# print("file=%s\n" % source_file)
# process.communicate(
#     'create database ciel; use ciel; source ' + source_file)

print("Import complete")
