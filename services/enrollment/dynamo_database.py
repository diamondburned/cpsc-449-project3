import boto3


def get_dynamodb_table(table_name: str):
    """
    Get a DynamoDB table resource.
    """
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:5600",  # Use the appropriate endpoint URL for DynamoDB Local
    )
    table = dynamodb.Table(table_name)
    return table


def get_department_details(department_table, department_id):
    """
    Retrieve department details based on the department ID.
    """
    response_department = department_table.query(
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": int(department_id)},
    )
    department_items = response_department.get("Items", [])
    return department_items[0] if department_items else None

def format_course(course, department_data):
    """
    Format the course item based on the department details.
    """
    return {
        "id": course.get("id"),
        "code": course.get("code"),
        "name": course.get("name"),
        "department": {
            "id": department_data.get("id"),
            "name": department_data.get("name"),
        },
    }

def get_courses_with_departments(course_id=None):
    courses_table = get_dynamodb_table("Course")
    department_table = get_dynamodb_table("Department")

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
        department_data = get_department_details(department_table, department_id)

        # If department_data is not None, format the course item
        if department_data:
            formatted_course = format_course(item, department_data)
            formatted_courses.append(formatted_course)

    return formatted_courses
