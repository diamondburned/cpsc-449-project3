from typing import Generator
import boto3
import mypy_boto3_dynamodb
from fastapi import Depends
from .models import *
from dotenv import load_dotenv
from .waitlist import WaitlistManager, get_waitlist_manager
from datetime import datetime

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


def get_section_enrollments(db: DynamoDB, section_id, status):
    enrollments_table = db.Table("Enrollment")
    user_table = db.Table("User")

    response_enrollments = enrollments_table.scan(
        FilterExpression="section_id = :section_id and #status = :enrolled",
        ExpressionAttributeValues={":section_id": int(section_id), ":enrolled": status},
        ExpressionAttributeNames={"#status": "status"},
    )

    enrollments = response_enrollments.get("Items", [])

    # Fetch user data and remove unnecessary fields for each enrollment
    for enrollment in enrollments:
        user_id = enrollment.get("user_id")
        if user_id:
            response_user = user_table.get_item(Key={"id": user_id})
            user_data = response_user.get("Item", {})
            enrollment["user"] = user_data

        # Remove unnecessary fields
        enrollment.pop("section_id", None)
        enrollment.pop("user_id", None)
        enrollment.pop("status", None)
        enrollment.pop("date", None)

    return enrollments

def get_user_enrollments(db: DynamoDB, user_id, status):
    enrollments_table = db.Table("Enrollment")

    response_enrollments = enrollments_table.query(
        KeyConditionExpression="user_id = :user_id",
        FilterExpression="#status = :status",
        ExpressionAttributeValues={":user_id": int(user_id), ":status": status},
        ExpressionAttributeNames={"#status": "status"},
    )

    enrollments = response_enrollments.get("Items", [])

    # Fetch user data and remove unnecessary fields for each enrollment
    for enrollment in enrollments:
        section_id = enrollment.get("section_id")
        if section_id:
            response_section = get_sections(db, section_id)
            section_data = response_section[0] if response_section else {}
            enrollment["section"] = section_data

        # Remove unnecessary fields
        enrollment.pop("date", None)
        enrollment.pop("section_id", None)

    return enrollments


def get_sections_for_user(db: DynamoDB, user_id: int):
    sections_table = db.Table("Section")

    # Use query to retrieve sections for a specific instructor_id
    response_sections = sections_table.query(
        IndexName="CourseInstructor",  # Specify the global secondary index
        KeyConditionExpression="instructor_id = :instructor_id",
        ExpressionAttributeValues={":instructor_id": user_id},
    )

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

def get_section_enrollments_count(db: DynamoDB, section_id, status):
    enrollments_table = db.Table("Enrollment")

    response_enrollments = enrollments_table.scan(
        FilterExpression="section_id = :section_id and #status = :status",
        ExpressionAttributeValues={":section_id": int(section_id), ":status": status},
        ExpressionAttributeNames={"#status": "status"},
    )

    enrollments_count = len(response_enrollments.get("Items", []))

    return enrollments_count

def check_section_full(db: DynamoDB, section_id: int):
    sections_table = db.Table("Section")

    response_sections = sections_table.scan(
        FilterExpression="id = :section_id",
        ExpressionAttributeValues={":section_id": int(section_id)},
    )
    sections = response_sections.get("Items", [])
    section = sections[0]

    section_capacity = section["capacity"]
    enrollment_count = get_section_enrollments_count(db, section_id, "Enrolled")

    return enrollment_count >= section_capacity

def check_waitlist_full(db: DynamoDB, section_id: int):
    sections_table = db.Table("Section")

    response_sections = sections_table.scan(
        FilterExpression="id = :section_id",
        ExpressionAttributeValues={":section_id": int(section_id)},
    )
    sections = response_sections.get("Items", [])
    section = sections[0]

    waitlist_capacity = section["waitlist_capacity"]
    
    waitlist = WaitlistManager()
    waitlist_count = waitlist.get_waitlist_count_for_section(section_id)

    return waitlist_count >= waitlist_capacity

def check_user_exists(db: DynamoDB, user_id: int) -> bool:
    user_table = db.Table("User")

    response_user = user_table.get_item(Key={"id": user_id})
    user_data = response_user.get("Item", {})

    return bool(user_data)

def enroll_in_section_as(db: DynamoDB, user_id: int, section_id: int, status):
    enrollments_table = db.Table("Enrollment")

    new_enrollment = {
        "user_id": user_id,
        "section_id": section_id,
        "status": status,
        "grade": "",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    enrollments_table.put_item(Item=new_enrollment)

def add_to_waitlist(db: DynamoDB, user_id: int, section_id: int):
    enrollments_table = db.Table("Enrollment")

    new_enrollment = {
        "user_id": user_id,
        "section_id": section_id,
        "status": "Enrolled",
        "grade": "",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    enrollments_table.put_item(Item=new_enrollment)

def get_course_id_for_section(db: DynamoDB, section_id: int) -> int:
    sections_table = db.Table("Section")

    response_sections = sections_table.scan(
        FilterExpression="id = :section_id",
        ExpressionAttributeValues={":section_id": int(section_id)},
    )
    sections = response_sections.get("Items", [])
    section = sections[0]

    return section["course_id"]

def get_enrollment(db: DynamoDB, user_id: int, section_id: int) -> dict:
    enrollments_table = db.Table("Enrollment")

    response_enrollment = enrollments_table.get_item(Key={"user_id": user_id, "section_id": section_id})
    enrollment_data = response_enrollment.get("Item", {})
    enrollment_data.pop("section_id", None)
    enrollment_data.pop("date", None)

    section = get_sections(db, section_id)
    enrollment_data['section'] = section[0]
    
    return enrollment_data

def create_section(db: DynamoDB, section):
    section_table = db.Table("Section")
    section_table.put_item(Item=section)


def update_section_by_id(db: DynamoDB, course_id, section_id, updated_values):
    section_table = db.Table("Section")

    # Build the update expression and attribute values
    update_expression = "SET "
    expression_attribute_values = {}

    updated_values.pop("course_id", None)

    for key, value in updated_values.items():
        attribute_name = f"#{key}"  # Use expression attribute name to handle reserved keywords
        update_expression += f"{attribute_name} = :{key}, "
        expression_attribute_values[attribute_name] = value

    update_expression = update_expression.rstrip(", ")  # Remove trailing comma

    # Update the section in DynamoDB
    response = section_table.update_item(
        Key={"course_id": course_id, "id": section_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues={f":{key}": expression_attribute_values[f"#{key}"] for key in updated_values},
        ExpressionAttributeNames={f"#{key}": key for key in updated_values},
        ReturnValues="UPDATED_NEW",  # Specify the response format
    )

    # Return the updated section
    updated_section = response.get("Attributes", {})
    return updated_section
