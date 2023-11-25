from typing import Generator
import boto3
import mypy_boto3_dynamodb
from fastapi import Depends
from dotenv import load_dotenv
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


def get_total_users_count(db: DynamoDB) -> int:
    user_table = db.Table("User")

    # Use scan to retrieve all items in the 'User' table
    response_users = user_table.scan()

    # Extract the items from the response
    users = response_users.get("Items", [])

    # Return the count of users
    return len(users)


def insert_user(db: DynamoDB, user_data):
    user_id = get_total_users_count(db) + 1
    user_data = {
        "id": user_id,
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "role": user_data.get("roles")[0].value,
        "username": user_data.get("username"),
    }

    user_table = db.Table("User")

    # Insert the new user into the User table
    user_table.put_item(Item=user_data)
    return user_id
