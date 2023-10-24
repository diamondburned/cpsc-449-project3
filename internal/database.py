from typing import Any, Generator, Iterable, Type
from fastapi import HTTPException
import contextlib
import sqlite3

sqlitePath: str | None = None


def set_db_path(path: str):
    global sqlitePath
    sqlitePath = path


sqlitePragma = """
-- Permit SQLite to be concurrently safe.
PRAGMA journal_mode = WAL;

-- Enable foreign key constraints.
PRAGMA foreign_keys = ON;

-- Enforce column types.
PRAGMA strict = ON;

-- Force queries to prefix column names with table names.
-- See https://www2.sqlite.org/cvstrac/wiki?p=ColumnNames.
PRAGMA full_column_names = ON;
PRAGMA short_column_names = OFF;
"""


def get_db(read_only=False) -> Generator[sqlite3.Connection, None, None]:
    """
    Get a new database connection.
    """
    assert sqlitePath is not None

    with sqlite3.connect(sqlitePath) as db:
        db.row_factory = sqlite3.Row

        # These pragmas are only relevant for write operations.
        cur = db.executescript(sqlitePragma)
        cur.close()

        try:
            yield db
        finally:
            if read_only:
                db.rollback()
            else:
                db.commit()


def get_readonly_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Get a read-only database connection.
    """
    return get_db(read_only=True)


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
