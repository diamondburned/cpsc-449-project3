from enum import Enum
from pydantic import BaseModel
from services.models import *


class Department(BaseModel):
    id: int
    name: str


class Course(BaseModel):
    id: int
    code: str
    name: str
    department: Department


class Section(BaseModel):
    id: int
    course: Course
    classroom: str | None
    capacity: int
    waitlist_capacity: int
    day: str
    begin_time: str
    end_time: str
    freeze: bool
    instructor_id: int


class EnrollmentStatus(str, Enum):
    ENROLLED = "Enrolled"
    WAITLISTED = "Waitlisted"
    DROPPED = "Dropped"


class Enrollment(BaseModel):
    user_id: int
    section: Section
    status: EnrollmentStatus
    grade: str | None


class Waitlist(BaseModel):
    user_id: int
    section: Section
    position: int
