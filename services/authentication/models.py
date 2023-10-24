from enum import Enum
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
