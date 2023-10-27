import argparse
import sqlite3
import pathlib
import os

from . import database, schema_testdata
from internal import password
from internal.database import init_db_cmd, write_row

init_db_cmd(
    schema_file=str(pathlib.Path(__file__).parent / "schema.sql"),
    db_path=database.rw_paths[0],
)

insertTestData = input("Insert test data? (y/N) ")
if insertTestData.lower() == "y":
    db = sqlite3.connect(database.rw_paths[0])
    db.row_factory = sqlite3.Row

    for i in range(len(schema_testdata.users)):
        id = i + 1
        user = schema_testdata.users[i]
        passhash = password.hash(user.password)

        write_row(
            db,
            """INSERT INTO users VALUES (?, ?, ?, ?, ?)""",
            (id, user.username, user.first_name, user.last_name, passhash),
        )

        for role in user.roles:
            write_row(
                db,
                """INSERT INTO user_roles VALUES (?, ?)""",
                (id, role),
            )

    db.commit()
    db.close()
