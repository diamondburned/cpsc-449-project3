from typing import Generator
import boto3
import mypy_boto3_dynamodb
from fastapi import Depends
from dotenv import load_dotenv
from datetime import datetime

from services.models import User

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


def insert_user(db: DynamoDB, user: User) -> None:
    user_table = db.Table("User")
    # Insert the new user into the User table
    user_table.put_item(Item=user.dict())
