from typing import Generator
import boto3
import mypy_boto3_dynamodb
from fastapi import Depends
from .models import *
from dotenv import load_dotenv

load_dotenv()

DynamoDB = mypy_boto3_dynamodb.DynamoDBServiceResource  # type alias


def get_dynamodb() -> Generator[DynamoDB, None, None]:
    """
    Get a DynamoDB table resource.
    """
    yield boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:5600",  # Use the appropriate endpoint URL for DynamoDB Local
        region_name="us-west-2",
    )


def get_department_details(db: DynamoDB, department_id):
    """
    Retrieve department details based on the department ID.
    """
    department_table = db.Table("Department")
    response_department = department_table.query(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": int(department_id)},
    )
    department_items = response_department.get("Items", [])
    return department_items[0] if department_items else None


def format_course(course, department_data) -> Course:
    """
    Format the course item based on the department details.
    """
    return Course(
        id=course.get("id"),
        code=course.get("code"),
        name=course.get("name"),
        department=Department(
            id=department_data.get("id"),
            name=department_data.get("name"),
            # Add other department attributes as needed
        ),
    )


def get_courses_with_departments(
    db: DynamoDB,
    course_id=None,
) -> list[Course]:
    courses_table = db.Table("Course")

    # Use query to retrieve a specific course if course_id is provided
    if course_id:
        response_courses = courses_table.query(
            KeyConditionExpression="id = :id",
            ExpressionAttributeValues={":id": int(course_id)},
        )
    else:
        # Use scan to retrieve all items in the 'Course' table
        response_courses = courses_table.scan()

    # Extract the items from the response
    courses = response_courses.get("Items", [])

    formatted_courses = []

    for item in courses:
        department_id = item.get("department_id")

        # Use the reusable function to get department details
        department_data = get_department_details(db, department_id)

        # If department_data is not None, format the course item
        if department_data:
            formatted_course = format_course(item, department_data)
            formatted_courses.append(formatted_course)

    return formatted_courses


def format_section(section, course):
    """
    Format the section item based on the course details.
    """
    print(section)
    return {
        "id": section.get("id"),
        "course": {
            "id": course.id,
            "code": course.code,
            "name": course.name,
            "department": {
                "id": course.department.id,
                "name": course.department.name,
            },
        },
        "classroom": section.get("classroom"),
        "capacity": int(section.get("capacity")),
        "waitlist_capacity": int(section.get("waitlist_capacity")),
        "day": section.get("day"),
        "begin_time": section.get("begin_time"),
        "end_time": section.get("end_time"),
        "freeze": bool(section.get("freeze")),
        "instructor_id": int(section.get("instructor_id")),
    }


def get_sections(db: DynamoDB, section_id=None) -> list[Course]:
    sections_table = db.Table("Section")

    # Use scan to retrieve a specific section if section_id is provided
    if section_id is not None:
        response_sections = sections_table.scan(
            FilterExpression="id = :section_id",
            ExpressionAttributeValues={":section_id": int(section_id)},
        )
    else:
        # Use scan to retrieve all items in the 'Section' table
        response_sections = sections_table.scan()

    # Extract the items from the response
    sections = response_sections.get("Items", [])

    formatted_sections = []

    for section in sections:
        # Get course information based on section's course_id
        courses = get_courses_with_departments(db, section.get("course_id"))
        if courses:
            course = courses[0]

            formatted_section = format_section(section, course)
            formatted_sections.append(formatted_section)

    return formatted_sections

def get_instructor(db: DynamoDB, instructor_id):
    instructor_table = db.Table("User")

    response_instructor = instructor_table.query(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": int(instructor_id)},
    )

    instructor_items = response_instructor.get("Items", [])

    return instructor_items[0] if instructor_items else None

def list_waitlist(db: DynamoDB, waitlist):
    for waitlist_item in waitlist:
        section_id = waitlist_item.get("section_id")
        section = get_sections(db, section_id)

        # Check if section information is available
        if section:
            # Remove section_id and course_id from the waitlist_item dictionary
            waitlist_item.pop("section_id", None)
            waitlist_item.pop("course_id", None)

            # Get instructor information based on section's instructor_id
            instructor_id = section[0].get("instructor_id")
            instructor = get_instructor(db, instructor_id)  # Implement get_instructor function

            # Add the section and instructor information to the waitlist item
            waitlist_item["section"] = section[0]  # Assuming get_sections returns a list
            waitlist_item["instructor"] = instructor  # Assuming get_instructor returns instructor info

            # Print the combined information
            print(waitlist_item)
        else:
            # If section information is not available, print the waitlist item as is
            print("Section not found for waitlist item:", waitlist_item)
    return waitlist