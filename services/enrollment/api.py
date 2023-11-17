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
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel

from internal.jwt_claims import require_x_roles, require_x_user

from . import database
from .dynamo_database import *
from .models import *
from .model_requests import *
from .waitlist import WaitlistManager, get_waitlist_manager

app = FastAPI()


# The API should allow students to:
#  - List available classes (/courses)
#  - Attempt to enroll in a class
#  - Drop a class
#
# Instructors should be able to:
#  - View current enrollment for their classes (/users/1/enrollments)
#  - View students who have dropped the class (/users/1/enrollments?status=Dropped)
#  - Drop students administratively (e.g. if they do not show up to class)
#
# The registrar should be able to:
#  - Add new classes and sections
#  - Remove existing sections
#  - Change the instructor for a section

# API draft:
#
# GET
#
# X /courses
# X /courses/1
# X /sections
# X /sections/1
# X /sections/1/enrollments
# X /sections/1/waitlist
# X /courses/1/waitlist
# X /users
# X /users/1/enrollments
# X /users/1/sections
# X /users/1/waitlist
#
# POST
#
# X /users/{user_id}/enrollments (enroll)
# X /courses (add course)
# X /sections (add section)
#
# PATCH
#
#   /sections/2 (change section, registrar only)
#
# DELETE
#
#   X /users/{user_id}/enrollments/{section_id} (drop enrollment)
#   X /users/{user_id}/waitlist/{section_id} (drop waitlist)
#   X /sections/{section_id}/enrollments/{user_id}
#     (drop enrollment,
#      instructor only,
#      just call /users' method though)
#   X /sections/{section_id} (remove section, registrar only)


@app.get("/courses")
def list_courses(db: DynamoDB = Depends(get_dynamodb)) -> ListCoursesResponse:
    courses = get_courses_with_departments(db)
    return ListCoursesResponse(courses=courses)


@app.get("/courses/{course_id}")
def get_course(course_id: int, db: DynamoDB = Depends(get_dynamodb)) -> Course:
    courses = get_courses_with_departments(db, course_id)
    if len(courses) == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    return courses[0]


@app.get("/courses/{course_id}/waitlist")
def get_course_waitlist(
    course_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    waitlist: WaitlistManager = Depends(get_waitlist_manager),
):
    course_waitlist = waitlist.get_waitlist_row_for_course(course_id)
    waitlist = list_waitlist(db, course_waitlist)
    return GetCourseWaitlistResponse(
        waitlist = list_waitlist(db, course_waitlist)
    )


@app.get("/sections")
def list_sections(
    db: DynamoDB = Depends(get_dynamodb),
) -> ListSectionsResponse:
    sections = get_sections(db)
    return ListSectionsResponse(
        sections=sections
    )


@app.get("/sections/{section_id}")
def get_section(
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
) -> Section:
    sections = get_sections(db, section_id)
    if len(sections) == 0:
        raise HTTPException(status_code=404, detail="Section not found")
    return sections[0]


@app.get("/sections/{section_id}/enrollments")
def list_section_enrollments(
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
):
    enrollments = get_section_enrollments(db, section_id, "Enrolled")
    return ListSectionEnrollmentsResponse(
        enrollments=enrollments
    )


@app.get("/sections/{section_id}/waitlist")
def list_section_waitlist(
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    waitlist: WaitlistManager = Depends(get_waitlist_manager),
) -> ListSectionWaitlistResponse:
    section_waitlist = waitlist.get_waitlist_row_for_section(section_id)

    return ListSectionWaitlistResponse(
        waitlist = list_waitlist(db, section_waitlist)
    )


@app.get("/users/{user_id}/enrollments")
def list_user_enrollments(
    user_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
)  -> ListUserEnrollmentsResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    user_enrollments = get_user_enrollments(db, user_id, "Enrolled")
    return ListUserEnrollmentsResponse(
        enrollments=user_enrollments
    )

@app.get("/users/{user_id}/sections")
def list_user_sections(
    user_id: int,
    db: DynamoDB = Depends(get_dynamodb),
) -> ListUserSectionsResponse:
    user_sections = get_sections_for_user(db,user_id)
    return ListUserSectionsResponse(
        sections=user_sections
    )


@app.get("/users/{user_id}/waitlist")
def list_user_waitlist(
    user_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> ListUserWaitlistResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    waitlist = WaitlistManager()
    user_waitlists = waitlist.get_waitlist_rows_for_user(user_id)

    return ListUserWaitlistResponse(
        waitlist=list_waitlist(db, user_waitlists)
    )

@app.post("/users/{user_id}/enrollments")  # student attempt to enroll in class
def create_enrollment(
    user_id: int,
    enrollment: CreateEnrollmentRequest,
    db: DynamoDB = Depends(get_dynamodb),
):

    user_exists = check_user_exists(db, user_id)
    
    if not user_exists:
        raise HTTPException(
                status_code=400,
                detail="User does not exist.",
            )
    
    
    section_id = enrollment.section
    section_exists = check_section_exists(db, section_id)
    if not section_exists:
        raise HTTPException(
                    status_code=400,
                    detail="Section does not exist.",
                )
    
    section_full = check_section_full(db, section_id)
    if not section_full:
        enroll_in_section_as(db, user_id, section_id, "Enrolled")
        enrollment = get_enrollment(db, user_id, section_id)
        return CreateEnrollmentResponse(
            user_id=enrollment["user_id"],
            section=enrollment["section"],
            status=enrollment["status"],
            grade=enrollment["grade"],
            waitlist_position=None,
        )
    else:
        waitlist_full = check_waitlist_full(db, section_id)
        if not waitlist_full:
            waitlist = WaitlistManager()
            waitlist_count_for_user = waitlist.get_waitlist_count_for_user(user_id)

            if waitlist_count_for_user < 3:
                course_id = get_course_id_for_section(db, section_id)
                waitlist_position = waitlist.add_to_waitlist(user_id, section_id, course_id)
                enroll_in_section_as(db, user_id, section_id, "Waitlisted")
                enrollment = get_enrollment(db, user_id, section_id)
                return CreateEnrollmentResponse(
                    user_id=enrollment["user_id"],
                    section=enrollment["section"],
                    status=enrollment["status"],
                    grade=enrollment["grade"],
                    waitlist_position=waitlist_position
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum number of waitlisted classes reached.",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Section is full and waitlist is full.",
            )



@app.post("/courses")
def add_course(
    course: AddCourseRequest,
    db: DynamoDB = Depends(get_dynamodb),
) -> Course:
    course = dict(course)
    create_course(db, course)
    course = get_courses_with_departments(db, course["id"])
    return course[0]

    
@app.post("/sections")
def add_section(
    section: AddSectionRequest,
    db: DynamoDB = Depends(get_dynamodb),
) -> Section:
    section = dict(section)
    create_section(db, section)
    section = get_sections(db, section["id"])
    return section[0]


@app.patch("/sections/{section_id}")
def update_section(
    section_id: int,
    section: UpdateSectionRequest,
    db: DynamoDB = Depends(get_dynamodb),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> Section:
    if Role.REGISTRAR not in jwt_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    section = dict(section)
    update_section_by_id(db, section["course_id"], section_id, section)
    section = get_sections(db, section_id)
    return section[0]


@app.delete("/users/{user_id}/enrollments/{section_id}")
def drop_user_enrollment(
    user_id: int,
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
) -> Enrollment:
    user_exists = check_user_exists(db, user_id)
    
    if not user_exists:
        raise HTTPException(
                status_code=400,
                detail="User does not exist.",
            )
    
    section_exists = check_section_exists(db, section_id)
    if not section_exists:
        raise HTTPException(
                    status_code=400,
                    detail="Section does not exist.",
                )
    
    user_enrolled = check_user_enrolled(db, user_id, section_id)
    if not user_enrolled:
        raise HTTPException(
                    status_code=400,
                    detail="User is not enrolled in section.",
                )
    

    mark_enrollment_as_dropped(db, user_id, section_id)
    enrollment = get_enrollment(db, user_id, section_id)
    return enrollment


@app.delete("/users/{user_id}/waitlist/{section_id}")
def drop_user_waitlist(
    user_id: int,
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    waitlist: WaitlistManager = Depends(get_waitlist_manager),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_exists = check_user_exists(db, user_id)
    if not user_exists:
        raise HTTPException(
                status_code=400,
                detail="User does not exist.",
            )
    
    section_exists = check_section_exists(db, section_id)
    if not section_exists:
        raise HTTPException(
                    status_code=400,
                    detail="Section does not exist.",
                )

    # Check if user is on the waitlist for a particular section
    user_on_waitlist_for_section = waitlist.check_user_on_waitlist_for_section(
        user_id, section_id
    )
    if not user_on_waitlist_for_section:
        raise HTTPException(
            status_code=400,
            detail="User is not on the waitlist.",
        )

    # Remove the user from the waitlist and return their position
    position = waitlist.remove_and_get_position(user_id, section_id)

    # Decrement the posistion of all the users that came after the user that was removed
    waitlist.decrement_positions_for_others(section_id, position)

    # Delete the waitlist enrollment form enrollments.
    delete_enrollment(db, user_id, section_id)
    return {"detail": "Successfully removed from waitlist"}


@app.delete("/sections/{section_id}/enrollments/{user_id}")
def drop_section_enrollment(
    section_id: int,
    user_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    section_exists = check_section_exists(db, section_id)
    if not section_exists:
        raise HTTPException(
                    status_code=400,
                    detail="Section does not exist.",
                )

    user_exists = check_user_exists(db, user_id)
    if not user_exists:
        raise HTTPException(
                status_code=400,
                detail="User does not exist.",
            )
    
    user_enrolled = check_user_enrolled(db, user_id, section_id)
    if not user_enrolled:
        raise HTTPException(
                    status_code=400,
                    detail="User is not enrolled in section.",
                )
    
    sections = get_sections(db, section_id)
    section = sections[0]
    instructor_id = section["instructor_id"]
    if instructor_id != jwt_user or Role.INSTRUCTOR not in jwt_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return drop_user_enrollment(user_id, section_id, db)


@app.delete("/sections/{section_id}")
def delete_section(
    section_id: int,
    db: DynamoDB = Depends(get_dynamodb),
    waitlist: WaitlistManager = Depends(get_waitlist_manager),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    section_exists = check_section_exists(db, section_id)
    if not section_exists:
        raise HTTPException(
                    status_code=400,
                    detail="Section does not exist.",
                )
    
    # check validity of section_id
    section = get_section(section_id, db)
    course_id = section.get("course").get("id")

    section = mark_section_as_deleted(db, course_id, section_id)

    all_enrollments = get_section_enrollments(db, section_id, "Enrolled")
    for enrollment in all_enrollments:
        user_id = enrollment.get("user").get("id")
        delete_enrollment(db, user_id, section_id)

    # drop waitlisted users
    waitlist.remove_all_in_section(section_id)
    return {"detail": "section successfully deleted."}


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
