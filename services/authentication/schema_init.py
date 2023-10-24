import argparse
import sqlite3
import pathlib
import os

from . import database
from internal.database import init_db_cmd

SQLITE_SCHEMA_FILE = pathlib.Path(__file__).parent / "schema.sql"
SQLITE_TESTDATA_FILE = pathlib.Path(__file__).parent / "schema_testdata.sql"

init_db_cmd(str(SQLITE_SCHEMA_FILE), str(SQLITE_TESTDATA_FILE))
