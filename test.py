import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

print("AWS_ACCESS_KEY_ID:", AWS_ACCESS_KEY_ID)
print('AWS_SECRET_ACCESS_KEY:', AWS_SECRET_ACCESS_KEY)
print('AWS_S3_BUCKET:', AWS_S3_BUCKET)

# Create S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='ap-south-2'  # Replace with your region
)

# Example: Upload a file to S3
file_name = 'example.txt'
s3_client.upload_file(file_name, AWS_S3_BUCKET, file_name)
print(f"Uploaded {file_name} to {AWS_S3_BUCKET}")