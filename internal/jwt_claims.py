"""
Code copied from Professor Kenytt Avery's
https://gist.github.com/ProfAvery/15992d20962b52e04523419df4939ea6.

All credit goes to him.
"""

import os
import sys
import json
import datetime
from typing import Optional

from pydantic import BaseModel
from services.models import Role


def expiration_in(minutes: int) -> tuple[datetime.datetime, datetime.datetime]:
    creation = datetime.datetime.now(tz=datetime.timezone.utc)
    expiration = creation + datetime.timedelta(minutes=minutes)
    return creation, expiration


class Claim(BaseModel):
    aud: str
    iss: str
    sub: str
    jti: str
    exp: int
    name: str
    roles: Optional[list[str]]


class Token(BaseModel):
    access_token: Claim
    refresh_token: Claim
    exp: int


def generate_claims(
    username: str,
    user_id: str,
    roles: list[Role],
    expiry_minutes=20,
) -> Token:
    _, exp = expiration_in(20)

    claims = Claim(
        aud="krakend.local.gd",
        iss="auth.local.gd",
        jti=generate_jti(),
        sub=str(user_id),
        name=username,
        roles=[role.value for role in roles],
        exp=int(exp.timestamp()),
    )
    token = Token(
        access_token=claims,
        refresh_token=claims,
        exp=int(exp.timestamp()),
    )

    return token


def generate_jti() -> str:
    return os.urandom(16).hex()
