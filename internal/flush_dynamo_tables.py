import boto3

# Initialize Boto3 DynamoDB resource with the appropriate endpoint URL for DynamoDB Local
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:5600'
)

def table_exists(table_name):
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    return table_name in existing_tables

def delete_table(table_name):
    try:
        if table_exists(table_name):
            table = dynamodb.Table(table_name)
            table.delete()
    except Exception as e:
        print(f"Error deleting table '{table_name}': {e}")

# Delete all tables
delete_table("User")
delete_table("Department")
delete_table("Course")
delete_table("Enrollment")
delete_table("Section")
delete_table("Waitlist")

print("Flushed existing data from dynamodb.")
