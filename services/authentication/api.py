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
    fetch_rows,
    fetch_row,
    write_row,
)
from internal import jwt_claims, password
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException

from . import database
from .database import get_db, get_read_db, get_user_roles
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
    user_row = fetch_row(
        db,
        "SELECT id, passhash FROM users WHERE username = ?",
        (req.username,),
    )
    if user_row is None:
        raise HTTPException(status_code=404, detail="User not found")

    id = extract_row(user_row, "users")["id"]

    passhash = extract_row(user_row, "users")["passhash"]
    if not password.verify(req.password, passhash):
        raise HTTPException(status_code=401, detail="Invalid password")

    roles = get_user_roles(db, id)

    return jwt_claims.generate_claims(
        username=req.username,
        user_id=id,
        roles=roles,
    )


class RegisterRequest(BaseModel):
    username: str
    password: str
    roles: list[Role]
    first_name: str
    last_name: str


class RegisterResponse(BaseModel):
    id: int


@app.post("/register")
def register(
    req: RegisterRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> RegisterResponse:
    passhash = password.hash(req.password)

    user_row = fetch_row(
        db,
        """
        INSERT INTO users (username, passhash, first_name, last_name)
        VALUES (?, ?, ?, ?)
        RETURNING id
        """,
        (req.username, passhash, req.first_name, req.last_name),
    )

    assert user_row is not None
    id = extract_row(user_row, "users")["id"]

    for role in req.roles:
        write_row(
            db,
            """
            INSERT INTO user_roles (user_id, role)
            VALUES (?, ?)
            """,
            (id, role),
        )

    return RegisterResponse(id=id)


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

    roles = get_user_roles(db, id)
    return User(**extract_row(user_row, "users"), roles=roles)


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
