import os
import contextlib
import sqlite3
from typing import Any, Generator, Iterable, Type
from fastapi import HTTPException

sqlite_path: str | None = None


def set_db_path(path: str):
    global sqlite_path
    sqlite_path = path


sqlitePragma = """
-- Permit SQLite to be concurrently safe.
PRAGMA journal_mode = WAL;

-- Enable foreign key constraints.
PRAGMA foreign_keys = ON;

-- Enforce column types.
PRAGMA strict = ON;
"""

sqlitePragmaRead = """
-- Force queries to prefix column names with table names.
-- See https://www2.sqlite.org/cvstrac/wiki?p=ColumnNames.
PRAGMA full_column_names = ON;
PRAGMA short_column_names = OFF;
"""


def get_db(
    db_path=sqlite_path,
    read_only=False,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Get a new database connection.
    """
    assert db_path is not None

    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        db.executescript(sqlitePragmaRead + (sqlitePragma if not read_only else ""))

        yield db


def get_read_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Get a read-only database connection.
    """
    yield from get_db(read_only=True)


def fetch_rows(
    db: sqlite3.Connection,
    sql: str,
    params: Any = None,
) -> list[sqlite3.Row]:
    cursor = db.execute(sql, params if params is not None else ())
    rows = cursor.fetchall()
    cursor.close()
    return [row for row in rows]


def fetch_row(
    db: sqlite3.Connection,
    sql: str,
    params: Any = None,
) -> sqlite3.Row | None:
    cursor = db.execute(sql, params if params is not None else ())
    row = cursor.fetchone()
    cursor.close()
    return row


def write_row(
    db: sqlite3.Connection,
    sql: str,
    params: Any = None,
):
    try:
        cursor = db.execute(sql, params if params is not None else ())
        cursor.close()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=str(e))


def extract_dict(d: dict, prefix: str) -> dict:
    """
    Extracts all keys from a dictionary that start with a given prefix.
    This is useful for extracting all keys from a dictionary that start with
    a given prefix, such as "user_" or "course_".
    """
    return {k[len(prefix) :]: v for k, v in d.items() if k.startswith(prefix)}


def extract_row(row: sqlite3.Row, table: str) -> dict:
    """
    Extracts all keys from a row that originate from a given table.
    """
    return extract_dict(dict(row), table + ".")


def exclude_dict(d: dict, keys: Iterable[str]) -> dict:
    """
    Returns a copy of a dictionary without the given keys.
    """
    return {k: v for k, v in d.items() if k not in keys}


def init_db_cmd(
    schema_file: str,
    testdata_file: str | None = None,
    db_path=sqlite_path,
):
    """
    Executes an interactive command to initialize the database with
    the given schema and test data.
    """
    assert db_path is not None

    schema_sql_file = open(schema_file, "r")
    schema_sql = schema_sql_file.read()

    schema_testdata_sql = None
    if testdata_file is not None:
        schema_testdata_sql_file = open(testdata_file, "r")
        schema_testdata_sql = schema_testdata_sql_file.read()

    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    if os.path.isfile(db_path):
        answer = input("Database file already exists. Overwrite? (y/N) ")
        if answer.lower() == "y":
            os.remove(db_path)
        else:
            print("Aborting...")
            exit(1)

    conn = sqlite3.connect(db_path)

    c = conn.cursor()
    c.executescript(schema_sql)

    if schema_testdata_sql is not None:
        insertTestData = input("Insert test data? (y/N) ")
        if insertTestData.lower() == "y":
            c.executescript(schema_testdata_sql)

    conn.commit()
    conn.close()
