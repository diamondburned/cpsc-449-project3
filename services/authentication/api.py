import collections
import contextlib
import logging.config
import secrets
import base64
import time
import sqlite3
from typing import Optional

from internal.database import extract_row, get_db, fetch_rows, fetch_row, write_row
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException

from . import database
from .models import *


app = FastAPI()


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
