from pydantic import BaseModel

from .models import *


class ListCoursesResponse(BaseModel):
    courses: list[Course]


class GetCourseWaitlistResponse(BaseModel):
    waitlist: list[Waitlist]


class ListSectionsResponse(BaseModel):
    sections: list[Section]


class ListUserSectionsType(str, Enum):
    ALL = "all"
    ENROLLED = "enrolled"
    INSTRUCTING = "instructing"


class CreateEnrollmentRequest(BaseModel):
    section: int


class CreateEnrollmentResponse(Enrollment):
    waitlist_position: int | None


class AddCourseRequest(BaseModel):
    id: int
    code: str
    name: str
    department_id: int


class AddSectionRequest(BaseModel):
    id: int
    course_id: int
    classroom: str
    capacity: int
    waitlist_capacity: int = 15
    day: str
    begin_time: str
    end_time: str
    freeze: bool = False
    instructor_id: int


class ListSectionEnrollmentsItem(BaseModel):
    user: User
    grade: str


class ListSectionEnrollmentsResponse(BaseModel):
    enrollments: list[ListSectionEnrollmentsItem]


class ListSectionWaitlistResponse(BaseModel):
    waitlist: list[Waitlist]


class ListUserEnrollmentsResponse(BaseModel):
    enrollments: list[Enrollment]


class ListUserSectionsResponse(BaseModel):
    sections: list[Section]


class ListUserWaitlistResponse(BaseModel):
    waitlist: list[Waitlist]


class UpdateSectionRequest(BaseModel):
    course_id: int
    classroom: str | None
    capacity: int | None
    waitlist_capacity: int | None
    day: str | None
    begin_time: str | None
    end_time: str | None
    freeze: bool | None
    instructor_id: int | None
