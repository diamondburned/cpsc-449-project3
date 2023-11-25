from enum import Enum
from pydantic import BaseModel


class Role(str, Enum):
    STUDENT = "Student"
    REGISTRAR = "Registrar"
    INSTRUCTOR = "Instructor"


class User(BaseModel):
    id: int
    username: str
    roles: list[Role]
    first_name: str
    last_name: str
