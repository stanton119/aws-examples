import boto3
import requests

# download csv
FILE_NAME = "car_data.csv"
response = requests.get("https://raw.githubusercontent.com/ACloudGuru-Resources/Course_AWS_Certified_Machine_Learning/master/Chapter5/car_data.csv")
with open(FILE_NAME, 'wb') as f:
    f.writelines(response.content)

# upload to s3

# create bucket
BUCKET_NAME = "quicksight_bucket"

s3_client = boto3.client('s3')
s3_client.upload_file(FILE_NAME, bucket, object_name)

with open(FILE_NAME, "rb") as f:
    s3.upload_fileobj(f, BUCKET_NAME, FILE_NAME)
