# coding: utf-8
import boto3
session = boto3.Session(profile=pythonAutomation)
session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')
bucket = s3.create_bucket(Bucket='aws-auto-videolyser', CreateBucketConfiguration={'LocationConstraint':session.region_name})
from pathlib import Path
pathname = 'C:/Users/adam.wickenden/OneDrive - Accenture/Downloads/Pexels Videos 1466210.mp4'
path = Path(pathname).expanduser().resolve()
print path
print(path)
bucket.upload_file(str(path), str(path.name))
rek_client = session.client('rekognition')
response = rekognition_client.start_label_detection(Video={'S3Object':{'Bucket':bucket.name,'Name':path.name}})
response = rek_client.start_label_detection(Video={'S3Object':{'Bucket':bucket.name,'Name':path.name}})
response
job_id = response['JobId']
result = rek_client.get_label_detection(JobId=job_id)
result
result.keys()
result[JobStatus]
result['JobStatus']
result['ResponseMetadta']
result['ResponseMetadata']
result['labels']
result['Labels']
len(result['Labels'])
