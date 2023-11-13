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
from .waitlist import WaitlistManager

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


# @app.get("/courses")
# def list_courses(
#     db: sqlite3.Connection = Depends(get_db),
# ) -> ListCoursesResponse:
#     return ListCoursesResponse(courses=database.list_courses(db))


@app.get("/courses")
def list_courses() -> ListCoursesResponse:
    courses = get_courses_with_departments()
    return ListCoursesResponse(courses=courses)


@app.get("/courses/{course_id}")
def get_course(
    course_id: int
) -> Course:
    courses = get_courses_with_departments(course_id)
    if len(courses) == 0:
            raise HTTPException(status_code=404, detail="Course not found")
    return courses[0]


@app.get("/courses/{course_id}/waitlist")
def get_course_waitlist(
    course_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    waitlist = WaitlistManager()
    rows = waitlist.get_waitlist_row_for_course(course_id)

    return GetCourseWaitlistResponse(
        waitlist=database.list_waitlist(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
            [row for row in rows],
        )
    )


# @app.get("/sections")
# def list_sections(
#     course_id: Optional[int] = None,
#     db: sqlite3.Connection = Depends(get_db),
# ) -> ListSectionsResponse:
#     section_ids = fetch_rows(
#         db,
#         """
#         SELECT id
#         FROM sections
#         WHERE deleted = FALSE
#         """
#         + ("" if course_id is None else "AND course_id = :course_id"),
#         {"course_id": course_id},
#     )
#     return ListSectionsResponse(
#         sections=database.list_sections(db, [row["sections.id"] for row in section_ids])
#     )
    
@app.get("/sections")
def list_sections(
    course_id: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db),
):
    sections = get_sections(course_id)
    return {"test": sections}


@app.get("/sections/{section_id}")
def get_section(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Section:
    sections = database.list_sections(db, [section_id])
    if len(sections) == 0:
        raise HTTPException(status_code=404, detail="Section not found")
    return sections[0]


@app.get("/sections/{section_id}/enrollments")
def list_section_enrollments(
    section_id: int,
    status=EnrollmentStatus.ENROLLED,
    db: sqlite3.Connection = Depends(get_db),
) -> ListSectionEnrollmentsResponse:
    rows = fetch_rows(
        db,
        """
        SELECT enrollments.user_id, enrollments.section_id
        FROM enrollments
        INNER JOIN sections ON sections.id = enrollments.section_id
        WHERE
            enrollments.status = ?
            AND sections.deleted = FALSE
            AND sections.id = ?
        """,
        (status, section_id),
    )
    rows = [extract_row(row, "enrollments") for row in rows]
    enrollments = database.list_enrollments(
        db,
        [(row["user_id"], row["section_id"]) for row in rows],
    )
    return ListSectionEnrollmentsResponse(
        enrollments=[
            ListSectionEnrollmentsItem(**dict(enrollment)) for enrollment in enrollments
        ]
    )


@app.get("/sections/{section_id}/waitlist")
def list_section_waitlist(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> ListSectionWaitlistResponse:
    waitlist = WaitlistManager()
    rows = waitlist.get_waitlist_row_for_section(section_id)

    return ListSectionWaitlistResponse(
        waitlist=database.list_waitlist(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
            [row for row in rows],
        )
    )


@app.get("/users/{user_id}/enrollments")
def list_user_enrollments(
    user_id: int,
    status=EnrollmentStatus.ENROLLED,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> ListUserEnrollmentsResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    rows = fetch_rows(
        db,
        """
        SELECT enrollments.user_id, enrollments.section_id
        FROM enrollments
        INNER JOIN sections ON sections.id = enrollments.section_id
        WHERE
            enrollments.status = ?
            AND sections.deleted = FALSE
            AND enrollments.user_id = ?
        """,
        (status, user_id),
    )
    rows = [extract_row(row, "enrollments") for row in rows]
    return ListUserEnrollmentsResponse(
        enrollments=database.list_enrollments(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
        )
    )


@app.get("/users/{user_id}/sections")
def list_user_sections(
    user_id: int,
    type: ListUserSectionsType = ListUserSectionsType.ALL,
    db: sqlite3.Connection = Depends(get_db),
) -> ListUserSectionsResponse:
    q = """
        SELECT sections.id
        FROM sections
        INNER JOIN enrollments ON enrollments.section_id = sections.id
        WHERE sections.deleted = FALSE AND
    """

    wheres = []
    q += "("
    if type == ListUserSectionsType.ALL or type == ListUserSectionsType.ENROLLED:
        wheres.append("enrollments.user_id = :user_id")
    if type == ListUserSectionsType.ALL or type == ListUserSectionsType.INSTRUCTING:
        wheres.append("sections.instructor_id = :user_id")
    q += " OR ".join(wheres)
    q += ")"

    rows = fetch_rows(db, q, {"user_id": user_id})
    return ListUserSectionsResponse(
        sections=database.list_sections(db, [row["sections.id"] for row in rows])
    )


@app.get("/users/{user_id}/waitlist")
def list_user_waitlist(
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> ListUserWaitlistResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    waitlist = WaitlistManager()
    rows = waitlist.get_waitlist_rows_for_user(user_id)

    return ListUserWaitlistResponse(
        waitlist=database.list_waitlist(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
            [row for row in rows],
        )
    )


@app.post("/users/{user_id}/enrollments")  # student attempt to enroll in class
def create_enrollment(
    user_id: int,
    enrollment: CreateEnrollmentRequest,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> CreateEnrollmentResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    d = {
        "user": user_id,
        "section": enrollment.section,
    }

    waitlist_position = None

    # Verify that the class still has space.
    id = fetch_row(
        db,
        """
        SELECT id
        FROM sections as s
        WHERE s.id = :section
        AND s.capacity > (SELECT COUNT(*) FROM enrollments WHERE section_id = :section)
        AND s.freeze = FALSE
        AND s.deleted = FALSE
        """,
        d,
    )
    if id:
        # If there is space, enroll the student.
        write_row(
            db,
            """
            INSERT INTO enrollments (user_id, section_id, status, grade, date)
            VALUES(:user, :section, 'Enrolled', NULL, CURRENT_TIMESTAMP)
            """,
            d,
        )
    else:
        waitlist = WaitlistManager()

        waitlist_count_for_section = waitlist.get_waitlist_count_for_section(
            enrollment.section
        )
        d["waitlist_count_for_section"] = waitlist_count_for_section

        waitlist_count_for_user = waitlist.get_waitlist_count_for_user(user_id)
        d["waitlist_count_for_user"] = waitlist_count_for_user

        # Otherwise, try to add them to the waitlist.
        id = fetch_row(
            db,
            """
            SELECT id
            FROM sections as s
            WHERE s.id = :section
            AND s.waitlist_capacity > :waitlist_count_for_section
            AND :waitlist_count_for_user < 3
            AND s.freeze = FALSE
            AND s.deleted = FALSE
            """,
            d,
        )
        if id:
            row = fetch_row(
                db,
                """
                SELECT course_id
                FROM sections as s
                WHERE s.id = :section
                """,
                d,
            )
            course_id = dict(row)["sections.course_id"]
            waitlist_position = waitlist.add_to_waitlist(
                user_id, enrollment.section, course_id, waitlist_count_for_section
            )

            # Ensure that there's also a waitlist enrollment.
            write_row(
                db,
                """
                INSERT INTO enrollments (user_id, section_id, status, grade, date)
                VALUES(:user, :section, 'Waitlisted', NULL, CURRENT_TIMESTAMP)
                """,
                d,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Section is full and waitlist is full.",
            )

    enrollments = database.list_enrollments(db, [(d["user"], d["section"])])
    return CreateEnrollmentResponse(
        **dict(enrollments[0]),
        waitlist_position=waitlist_position,
    )


@app.post("/courses")
def add_course(
    course: AddCourseRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Course:
    try:
        row = fetch_row(
            db,
            """
            INSERT INTO courses(code, name, department_id)
            VALUES(:code, :name, :department_id)
            RETURNING id
            """,
            dict(course),
        )
        assert row
        courses = database.list_courses(db, [row["courses.id"]])
        return courses[0]
    except Exception:
        raise HTTPException(status_code=409, detail=f"Failed to add course:")


@app.post("/sections")
def add_section(
    section: AddSectionRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Section:
    try:
        row = fetch_row(
            db,
            """
            INSERT INTO sections(course_id, classroom, capacity, waitlist_capacity, day, begin_time, end_time, freeze, instructor_id)
            VALUES(:course_id, :classroom, :capacity, :waitlist_capacity, :day, :begin_time, :end_time, :freeze, :instructor_id)
            RETURNING id
            """,
            dict(section),
        )
        assert row
        sections = database.list_sections(db, [row["sections.id"]])
        return sections[0]
    except Exception:
        raise HTTPException(status_code=409, detail=f"Failed to add course:")


@app.patch("/sections/{section_id}")
def update_section(
    section_id: int,
    section: UpdateSectionRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Section:
    q = """
    UPDATE sections
    SET
    """
    v = {}
    for key, value in section.dict().items():
        if value is not None:
            q += f"{key} = :{key}, "
            v[key] = value

    if len(v) == 0:
        raise HTTPException(
            status_code=400,
            detail="No fields provided to update.",
        )

    q = q[:-2]  # remove trailing comma

    q += """
    WHERE id = :section_id
    """
    v["section_id"] = section_id

    try:
        write_row(db, q, v)
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Failed to update section:{e}")

    sections = database.list_sections(db, [section_id])
    return sections[0]


@app.delete("/users/{user_id}/enrollments/{section_id}")
def drop_user_enrollment(
    user_id: int,
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Enrollment:
    write_row(
        db,
        """
        UPDATE enrollments
        SET status = 'Dropped'
        WHERE
            user_id = :user_id
            AND section_id = :section_id
            AND status = 'Enrolled'
        """,
        {"user_id": user_id, "section_id": section_id},
    )

    enrollments = database.list_enrollments(db, [(user_id, section_id)])
    return enrollments[0]


@app.delete("/users/{user_id}/waitlist/{section_id}")
def drop_user_waitlist(
    user_id: int,
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    waitlist = WaitlistManager()

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

    # Delete the waitlist enrollment.
    write_row(
        db,
        """
        DELETE FROM enrollments
        WHERE
            user_id = :user_id
            AND section_id = :section_id
            AND status = 'Waitlisted'
        """,
        {"user_id": user_id, "section_id": section_id},
    )


@app.delete("/sections/{section_id}/enrollments/{user_id}")
def drop_section_enrollment(
    section_id: int,
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> Enrollment:
    # Ensure the user is instructing the section or is a registrar.
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        row = fetch_row(
            db,
            """
            SELECT instructor_id FROM sections
            WHERE id = :section_id
            """,
            {"section_id": section_id},
        )
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Section not found.",
            )
        if row["sections.instructor_id"] != jwt_user:
            raise HTTPException(status_code=403, detail="Not authorized")

    # No auth so these two methods behave virtually identically.
    return drop_user_enrollment(user_id, section_id, db)


@app.delete("/sections/{section_id}")
def delete_section(section_id: int, db: sqlite3.Connection = Depends(get_db)):
    # check validity of section_id
    get_section(section_id, db)

    # mark section as deleted
    write_row(
        db,
        """
        UPDATE sections
        SET deleted = TRUE
        WHERE id = :section_id
        """,
        {"section_id": section_id},
    )

    # drop enrolled users
    ue = fetch_rows(
        db,
        f"""
        SELECT user_id FROM enrollments
        WHERE 
            section_id = :section_id
        """,
        {"section_id": section_id},
    )
    for u in ue:
        print(u)
        drop_user_enrollment(u[0], section_id, db)

    # drop waitlisted users
    waitlist = WaitlistManager()
    waitlist.remove_all_in_section(section_id)


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
