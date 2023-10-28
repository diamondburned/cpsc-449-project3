import os
import sqlite3
import internal.database
from typing import Generator
from dotenv import load_dotenv
from internal.database import fetch_rows, extract_row, set_db_path

from services.models import *

load_dotenv()

rw_paths = [
    "run/authentication/primary/fuse/auth.db",
]

ro_paths = [
    "run/authentication/secondary1/fuse/auth.db",
    "run/authentication/secondary2/fuse/auth.db",
]

ro_path = 0
rw_path = 0


def get_db() -> Generator[sqlite3.Connection, None, None]:
    global rw_path
    rw_path = (rw_path + 1) % len(rw_paths)
    db_path = rw_paths[rw_path]

    yield from internal.database.get_db(db_path)


def get_read_db() -> Generator[sqlite3.Connection, None, None]:
    global ro_path
    # TODO: fix ro_path so that it retries the next path if the current one
    # is down
    ro_path = (ro_path + 1) % len(ro_paths)
    db_path = ro_paths[ro_path]

    yield from internal.database.get_read_db(db_path)


def get_user_roles(db: sqlite3.Connection, user_id: int) -> list[Role]:
    role_rows = fetch_rows(
        db,
        "SELECT role FROM user_roles WHERE user_id = ?",
        (user_id,),
    )
    roles = [Role(row["user_roles.role"]) for row in role_rows]
    return roles
