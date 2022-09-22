import boto3
import requests

import app

FILE_NAME = "car_data.csv"


def download_csv():
    response = requests.get(
        "https://raw.githubusercontent.com/ACloudGuru-Resources/Course_AWS_Certified_Machine_Learning/master/Chapter5/car_data.csv"
    )
    if response.status_code == 200:
        with open(FILE_NAME, "wb") as f:
            f.write(response.content)


def upload_csv_to_s3():
    s3_client = boto3.client("s3")
    # s3_client.upload_file(FILE_NAME, app.BUCKET_NAME, object_name)
    with open(FILE_NAME, "rb") as f:
        s3_client.upload_fileobj(f, app.BUCKET_NAME, FILE_NAME)


if __name__ == "__main__":
    download_csv()
    upload_csv_to_s3()
