import boto3

# Initialize Boto3 DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:5600",  # Use the appropriate endpoint URL for DynamoDB Local
    region_name="us-west-2",
)

# Define user data
user_data = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "role": "Student",
        "username": "johndoe",
    },
    {
        "id": 2,
        "first_name": "Kenytt",
        "last_name": "Avery",
        "role": "Instructor",
        "username": "kenyttavery",
    },
    {
        "id": 3,
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "Registrar",
        "username": "janedoe",
    },
    {
        "id": 4,
        "first_name": "Bobby",
        "last_name": "Muir",
        "role": "Instructor",
        "username": "bobbymuir",
    },
    {
        "id": 5,
        "first_name": "Alice",
        "last_name": "Smith",
        "role": "Student",
        "username": "alicesmith",
    },
    {
        "id": 6,
        "first_name": "Bob",
        "last_name": "Jones",
        "role": "Student",
        "username": "bobjones",
    },
    {
        "id": 7,
        "first_name": "Carol",
        "last_name": "Williams",
        "role": "Student",
        "username": "carolwilliams",
    },
    {
        "id": 8,
        "first_name": "Dave",
        "last_name": "Brown",
        "role": "Student",
        "username": "davebrown",
    },
    {
        "id": 9,
        "first_name": "Eve",
        "last_name": "Miller",
        "role": "Student",
        "username": "evemiller",
    },
    {
        "id": 10,
        "first_name": "Frank",
        "last_name": "Davis",
        "role": "Student",
        "username": "frankdavis",
    },
    {
        "id": 11,
        "first_name": "Grace",
        "last_name": "Garcia",
        "role": "Student",
        "username": "gracegarcia",
    },
    {
        "id": 12,
        "first_name": "Henry",
        "last_name": "Rodriguez",
        "role": "Student",
        "username": "henryrodriguez",
    },
    {
        "id": 13,
        "first_name": "Isabel",
        "last_name": "Wilson",
        "role": "Student",
        "username": "isabelwilson",
    },
    {
        "id": 14,
        "first_name": "Jack",
        "last_name": "Martinez",
        "role": "Student",
        "username": "jackmartinez",
    },
]

# Define department data
department_data = [
    {"id": 1, "name": "Computer Science"},
    {"id": 2, "name": "Engineering"},
    {"id": 3, "name": "Mathematics"},
]

# Define course data
course_data = [
    {
        "id": 1,
        "code": "CPSC 449",
        "name": "Web Back-End Engineering",
        "department_id": 1,
    },
    {"id": 2, "code": "MATH 150A", "name": "Calculus I", "department_id": 3},
]

# Define section data
section_data = [
    {
        "id": 1,
        "course_id": 1,
        "classroom": "CS102",
        "capacity": 3,
        "waitlist_capacity": 15,
        "day": "Tuesday",
        "begin_time": "7pm",
        "end_time": "9:45pm",
        "instructor_id": 2,
        "freeze": False,
        "deleted": False,
    },
    {
        "id": 2,
        "course_id": 1,
        "classroom": "CS104",
        "capacity": 30,
        "waitlist_capacity": 15,
        "day": "Wednesday",
        "begin_time": "4pm",
        "end_time": "6:45pm",
        "instructor_id": 2,
        "freeze": False,
        "deleted": False,
    },
    {
        "id": 3,
        "course_id": 2,
        "classroom": "MH302",
        "capacity": 35,
        "waitlist_capacity": 15,
        "day": "Monday",
        "begin_time": "12pm",
        "end_time": "2:45pm",
        "instructor_id": 4,
        "freeze": False,
        "deleted": False,
    },
    {
        "id": 4,
        "course_id": 2,
        "classroom": "MH107",
        "capacity": 32,
        "waitlist_capacity": 15,
        "day": "Thursday",
        "begin_time": "9am",
        "end_time": "11:30am",
        "instructor_id": 4,
        "freeze": False,
        "deleted": False,
    },
]

# Define enrollment data
enrollment_data = [
    {
        "user_id": 5,
        "section_id": 1,
        "status": "Enrolled",
        "grade": "A",
        "date": "2023-09-15",
    },
    {
        "user_id": 6,
        "section_id": 1,
        "status": "Enrolled",
        "grade": "B",
        "date": "2023-09-15",
    },
    {
        "user_id": 7,
        "section_id": 1,
        "status": "Enrolled",
        "grade": "C",
        "date": "2023-09-15",
    },
    {
        "user_id": 8,
        "section_id": 1,
        "status": "Enrolled",
        "grade": "B+",
        "date": "2023-09-15",
    },
    {
        "user_id": 9,
        "section_id": 2,
        "status": "Enrolled",
        "grade": "A-",
        "date": "2023-09-15",
    },
    {
        "user_id": 10,
        "section_id": 2,
        "status": "Dropped",
        "grade": None,
        "date": "2023-09-15",
    },
    {
        "user_id": 11,
        "section_id": 2,
        "status": "Enrolled",
        "grade": "A+",
        "date": "2023-09-15",
    },
    {
        "user_id": 12,
        "section_id": 3,
        "status": "Enrolled",
        "grade": "C+",
        "date": "2023-09-15",
    },
    {
        "user_id": 13,
        "section_id": 3,
        "status": "Dropped",
        "grade": None,
        "date": "2023-09-15",
    },
    {
        "user_id": 14,
        "section_id": 4,
        "status": "Enrolled",
        "grade": "A-",
        "date": "2023-09-15",
    },
    {
        "user_id": 5,
        "section_id": 3,
        "status": "Enrolled",
        "grade": "B",
        "date": "2023-09-15",
    },
    {
        "user_id": 6,
        "section_id": 4,
        "status": "Enrolled",
        "grade": "B",
        "date": "2023-09-15",
    },
    {
        "user_id": 7,
        "section_id": 2,
        "status": "Enrolled",
        "grade": "B",
        "date": "2023-09-15",
    },
]

# Get references to DynamoDB tables
user_table = dynamodb.Table("User")
department_table = dynamodb.Table("Department")
course_table = dynamodb.Table("Course")
section_table = dynamodb.Table("Section")
enrollment_table = dynamodb.Table("Enrollment")

# Insert user data into the User table
for item in user_data:
    user_table.put_item(Item=item)

# Insert department data into the Department table
for item in department_data:
    department_table.put_item(Item=item)

# Insert course data into the Course table
for item in course_data:
    course_table.put_item(Item=item)

# Insert department data into the Department table
for item in section_data:
    section_table.put_item(Item=item)

# Insert enrollment data into the Enrollment table
for item in enrollment_data:
    enrollment_table.put_item(Item=item)

print("Data inserted successfully.")
