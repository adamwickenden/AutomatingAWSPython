# coding: utf-8
import boto3
from pathlib import Path

session = boto3.Session(profile_name="pythonAutomation")
s3 = session.resource("s3")
bucket = s3.create_bucket(
    Bucket="aws-auto-videolyser1234",
    CreateBucketConfiguration={"LocationConstraint": session.region_name},
)

pathname = (
    "C:/Users/adam.wickenden/OneDrive - Accenture/Downloads/Pexels Videos 1466210.mp4"
)
path = Path(pathname).expanduser().resolve()
print(path)
bucket.upload_file(str(path), str(path.name))
rek_client = session.client("rekognition")
response = rek_client.start_label_detection(
    Video={"S3Object": {"Bucket": bucket.name, "Name": path.name}}
)
response
job_id = response["JobId"]
result = rek_client.get_label_detection(JobId=job_id)


def make_item(data):
    if isinstance(data, dict):
        return {k: make_item(v) for k, v in data.items()}
    if isinstance(data, list):
        return [make_item(v) for v in data]
    if isinstance(data, float):
        return str(data)
    else:
        return data
