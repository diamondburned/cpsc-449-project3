from enum import Enum


class Role(str, Enum):
    STUDENT = "Student"
    REGISTRAR = "Registrar"
    INSTRUCTOR = "Instructor"
