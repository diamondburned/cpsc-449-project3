import boto3

# Initialize Boto3 DynamoDB resource with the appropriate endpoint URL for DynamoDB Local
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:5500'
)

def delete_table(table_name):
    try:
        table = dynamodb.Table(table_name)
        table.delete()
    except Exception as e:
        print(f"Error deleting table '{table_name}':  {e}")

# Delete all tables
delete_table("User")
delete_table("Department")
delete_table("Course")
delete_table("Enrollment")
delete_table("Section")

print("All tables deleted successfully.")