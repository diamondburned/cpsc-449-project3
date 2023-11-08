import boto3

# Initialize Boto3 DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:5500',  # Use the appropriate endpoint URL for DynamoDB Local
)

# Define user data
user_data = [
    {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'role': 'Student'
    },
    {
        'id': 2,
        'first_name': 'Kenytt',
        'last_name': 'Avery',
        'role': 'Instructor'
    },
    {
        'id': 3,
        'first_name': 'Jane',
        'last_name': 'Doe',
        'role': 'Registrar'
    },
    {
        'id': 4,
        'first_name': 'Bobby',
        'last_name': 'Muir',
        'role': 'Instructor'
    },
    {
        'id': 5,
        'first_name': 'Alice',
        'last_name': 'Smith',
        'role': 'Student'
    },
    {
        'id': 6,
        'first_name': 'Bob',
        'last_name': 'Jones',
        'role': 'Student'
    },
    {
        'id': 7,
        'first_name': 'Carol',
        'last_name': 'Williams',
        'role': 'Student'
    },
    {
        'id': 8,
        'first_name': 'Dave',
        'last_name': 'Brown',
        'role': 'Student'
    },
    {
        'id': 9,
        'first_name': 'Eve',
        'last_name': 'Miller',
        'role': 'Student'
    },
    {
        'id': 10,
        'first_name': 'Frank',
        'last_name': 'Davis',
        'role': 'Student'
    },
    {
        'id': 11,
        'first_name': 'Grace',
        'last_name': 'Garcia',
        'role': 'Student'
    },
    {
        'id': 12,
        'first_name': 'Henry',
        'last_name': 'Rodriguez',
        'role': 'Student'
    },
    {
        'id': 13,
        'first_name': 'Isabel',
        'last_name': 'Wilson',
        'role': 'Student'
    },
    {
        'id': 14,
        'first_name': 'Jack',
        'last_name': 'Martinez',
        'role': 'Student'
    }
]

# Define department data
department_data = [
    {
        'id': 1,
        'name': 'Computer Science'
    },
    {
        'id': 2,
        'name': 'Engineering'
    },
    {
        'id': 3,
        'name': 'Mathematics'
    }
]

# Define course data
course_data = [
    {
        'id': 1,
        'name': 'CPSC 449',
        'description': 'Web Back-End Engineering',
        'department_id': 1
    },
    {
        'id': 2,
        'name': 'MATH 150A',
        'description': 'Calculus I',
        'department_id': 3
    }
]

# Define section data
section_data = [
    {
        'id': 1,
        'course_id': 1,
        'section_code': 'CS102',
        'capacity': 30,
        'enrollment_count': 15,
        'day_of_week': 'Tuesday',
        'start_time': '7pm',
        'end_time': '9:45pm',
        'instructor': 2,
        'waitlist_count': 0,
        'waitlist_capacity': 0
    },
    {
        'id': 2,
        'course_id': 1,
        'section_code': 'CS104',
        'capacity': 30,
        'enrollment_count': 15,
        'day_of_week': 'Wednesday',
        'start_time': '4pm',
        'end_time': '6:45pm',
        'instructor': 2,
        'waitlist_count': 0,
        'waitlist_capacity': 0
    },
    {
        'id': 3,
        'course_id': 2,
        'section_code': 'MH302',
        'capacity': 35,
        'enrollment_count': 15,
        'day_of_week': 'Monday',
        'start_time': '12pm',
        'end_time': '2:45pm',
        'instructor': 4,
        'waitlist_count': 0,
        'waitlist_capacity': 0
    },
    {
        'id': 4,
        'course_id': 2,
        'section_code': 'MH107',
        'capacity': 32,
        'enrollment_count': 15,
        'day_of_week': 'Thursday',
        'start_time': '9am',
        'end_time': '11:30am',
        'instructor': 4,
        'waitlist_count': 0,
        'waitlist_capacity': 0
    }
]

# Define enrollment data
enrollment_data = [
    {
        'user_id': 5,
        'section_id': 1,
        'status': 'Enrolled',
        'grade': 'A',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 6,
        'section_id': 1,
        'status': 'Enrolled',
        'grade': 'B',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 7,
        'section_id': 1,
        'status': 'Enrolled',
        'grade': 'C',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 8,
        'section_id': 1,
        'status': 'Enrolled',
        'grade': 'B+',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 9,
        'section_id': 2,
        'status': 'Enrolled',
        'grade': 'A-',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 10,
        'section_id': 2,
        'status': 'Dropped',
        'grade': None,
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 11,
        'section_id': 2,
        'status': 'Enrolled',
        'grade': 'A+',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 12,
        'section_id': 3,
        'status': 'Enrolled',
        'grade': 'C+',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 13,
        'section_id': 3,
        'status': 'Dropped',
        'grade': None,
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 14,
        'section_id': 4,
        'status': 'Enrolled',
        'grade': 'A-',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 5,
        'section_id': 3,
        'status': 'Enrolled',
        'grade': 'B',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 6,
        'section_id': 4,
        'status': 'Enrolled',
        'grade': 'B',
        'enrollment_date': '2023-09-15'
    },
    {
        'user_id': 7,
        'section_id': 2,
        'status': 'Enrolled',
        'grade': 'B',
        'enrollment_date': '2023-09-15'
    }
]

# Get references to DynamoDB tables
user_table = dynamodb.Table('User')
department_table = dynamodb.Table('Department')
course_table = dynamodb.Table('Course')
section_table = dynamodb.Table('Section')
enrollment_table = dynamodb.Table('Enrollment')

# Insert user data into the User table
for item in user_data:
    user_table.put_item(Item=item)
print("User data inserted successfully.")

# Insert department data into the Department table
for item in department_data:
    department_table.put_item(Item=item)
print("Department data inserted successfully.")

# Insert course data into the Course table
for item in course_data:
    course_table.put_item(Item=item)
print("Course data inserted successfully.")

# Insert department data into the Department table
for item in section_data:
    section_table.put_item(Item=item)
print("Section data inserted successfully.")

# Insert enrollment data into the Enrollment table
for item in enrollment_data:
    enrollment_table.put_item(Item=item)
print("Enrollment data inserted successfully.")

print("Data inserted successfully.")
