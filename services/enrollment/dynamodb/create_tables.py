import boto3
from botocore.exceptions import ClientError

# Initialize Boto3 DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:5600",  # Use the appropriate endpoint URL for DynamoDB Local
)

# Create the User table with on-demand capacity mode
user_table = dynamodb.create_table(
    TableName="User",
    KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],  # Partition key
    AttributeDefinitions=[
        {"AttributeName": "id", "AttributeType": "N"},  # Number
    ],
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
)

# Create the Departments table with on-demand capacity mode
departments_table = dynamodb.create_table(
    TableName="Department",
    KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],  # Partition key
    AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],  # Number
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
)

# Create the Courses table with on-demand capacity mode
courses_table = dynamodb.create_table(
    TableName="Course",
    KeySchema=[
        {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "department_id", "KeyType": "RANGE"},  # Sort key
    ],
    AttributeDefinitions=[
        {"AttributeName": "id", "AttributeType": "N"},  # Number
        {"AttributeName": "department_id", "AttributeType": "N"},  # Number
        {"AttributeName": "code", "AttributeType": "S"},  # String
    ],
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
    GlobalSecondaryIndexes=[
        {
            "IndexName": "DepartmentIndex",
            "KeySchema": [
                {
                    "AttributeName": "department_id",
                    "KeyType": "HASH",  # Partition key for the secondary index
                },
                {
                    "AttributeName": "code",
                    "KeyType": "RANGE",  # Sort key for the secondary index
                },
            ],
            "Projection": {
                "ProjectionType": "ALL",  # The desired projection type
            },
        }
    ],
)


# Create the Enrollments table with on-demand capacity mode
enrollments_table = dynamodb.create_table(
    TableName="Enrollment",
    KeySchema=[
        {"AttributeName": "user_id", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "section_id", "KeyType": "RANGE"},  # Sort key
    ],
    AttributeDefinitions=[
        {"AttributeName": "user_id", "AttributeType": "N"},  # Number
        {"AttributeName": "section_id", "AttributeType": "N"},  # Number
    ],
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
)


# Create the Sections table with on-demand capacity mode and a secondary index
sections_table = dynamodb.create_table(
    TableName="Section",
    KeySchema=[
        {"AttributeName": "course_id", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "id", "KeyType": "RANGE"},  # Sort key
    ],
    AttributeDefinitions=[
        {"AttributeName": "id", "AttributeType": "N"},  # Number
        {"AttributeName": "course_id", "AttributeType": "N"},  # Number
        {"AttributeName": "instructor_id", "AttributeType": "N"},  # Number
    ],
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
    GlobalSecondaryIndexes=[
        {
            "IndexName": "CourseInstructor",  # Updated valid index name
            "KeySchema": [
                {
                    "AttributeName": "instructor_id",
                    "KeyType": "HASH",  # Partition key for the secondary index
                },
                {
                    "AttributeName": "course_id",
                    "KeyType": "RANGE",  # Sort key for the secondary index
                },
            ],
            "Projection": {
                "ProjectionType": "ALL",  # The desired projection type
            },
        }
    ],
)

# Create the Waitlist table with on-demand capacity mode
waitlist_table = dynamodb.create_table(
    TableName="Waitlist",
    KeySchema=[
        {"AttributeName": "user_id", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "section_id", "KeyType": "RANGE"},  # Sort key
    ],
    AttributeDefinitions=[
        {"AttributeName": "user_id", "AttributeType": "N"},  # Number
        {"AttributeName": "section_id", "AttributeType": "N"},  # Number
        {"AttributeName": "course_id", "AttributeType": "N"},  # Number
        {"AttributeName": "position", "AttributeType": "N"},  # Number
    ],
    BillingMode="PAY_PER_REQUEST",  # Set to on-demand capacity mode
    GlobalSecondaryIndexes=[
        {
            "IndexName": "CourseIndex",
            "KeySchema": [
                {
                    "AttributeName": "course_id",
                    "KeyType": "HASH",  # Partition key for the secondary index
                },
                {
                    "AttributeName": "position",
                    "KeyType": "RANGE",  # Sort key for the secondary index
                },
            ],
            "Projection": {
                "ProjectionType": "ALL",  # The desired projection type
            },
        }
    ],
)

print("Tables created successfully.")
