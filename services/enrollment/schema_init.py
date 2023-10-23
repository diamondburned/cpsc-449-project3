import argparse
import sqlite3
import pathlib
import os

from .database import SQLITE_DATABASE

SQLITE_SCHEMA_FILE = pathlib.Path(__file__).parent / "schema.sql"
SQLITE_TESTDATA_FILE = pathlib.Path(__file__).parent / "schema_testdata.sql"

if __name__ == "__main__":
    schema_sql_file = open(SQLITE_SCHEMA_FILE, "r")
    schema_sql = schema_sql_file.read()

    schema_testdata_sql_file = open(SQLITE_TESTDATA_FILE, "r")
    schema_testdata_sql = schema_testdata_sql_file.read()

    if os.path.isfile(SQLITE_DATABASE):
        answer = input("Database file already exists. Overwrite? (y/n) ")
        if answer.lower() == "y":
            os.remove(SQLITE_DATABASE)
        else:
            print("Aborting...")
            exit(1)

    conn = sqlite3.connect(SQLITE_DATABASE)

    c = conn.cursor()
    c.executescript(schema_sql)

    insertTestData = input("Insert test data? (y/n) ")
    if insertTestData.lower() == "y":
        c.executescript(schema_testdata_sql)

    conn.commit()
    conn.close()
