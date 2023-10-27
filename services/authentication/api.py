import collections
import contextlib
import logging.config
import secrets
import base64
import time
import sqlite3
from typing import Optional

from internal.database import (
    extract_row,
    get_db,
    get_read_db,
    fetch_rows,
    fetch_row,
    write_row,
)
from internal.password import hash as hash_password, verify as verify_password
from internal import jwt_claims
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException

from . import database
from services.models import *


app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(
    req: LoginRequest,
    db: sqlite3.Connection = Depends(get_read_db),
) -> jwt_claims.Token:
    # TODO: read user salt and hash from database
    # TODO: verify password
    # TODO: generate JWT claim
    raise NotImplementedError()


class RegisterRequest(BaseModel):
    username: str
    password: str
    roles: list[Role]
    first_name: str
    last_name: str


@app.post("/register")
def register(
    req: RegisterRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> None:
    passhash = hash_password(req.password)
    # TODO: insert into database
    raise NotImplementedError()


class User(BaseModel):
    id: int
    username: str
    roles: list[Role]
    first_name: str
    last_name: str


@app.get("/users/{id}")
def get_user(id: int, db: sqlite3.Connection = Depends(get_read_db)) -> User:
    user_row = fetch_row(
        db,
        "SELECT id, username, first_name, last_name FROM users WHERE id = ?",
        (id,),
    )
    if user_row is None:
        raise HTTPException(status_code=404, detail="User not found")

    role_rows = fetch_rows(db, "SELECT role FROM roles WHERE user_id = ?", (id,))
    roles = [Role(row["roles.role"]) for row in role_rows]

    return User(**extract_row(user_row, "users"), roles=roles)


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
