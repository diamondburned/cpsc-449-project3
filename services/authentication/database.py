import os
from internal.database import fetch_rows, extract_row, set_db_path
from dotenv import load_dotenv

load_dotenv()

AUTHENTICATION_DATABASE = os.getenv("AUTHENTICATION_DATABASE")
if AUTHENTICATION_DATABASE is None:
    raise Exception("$AUTHENTICATION_DATABASE is not set")

set_db_path(AUTHENTICATION_DATABASE)
