import urllib
import boto3
import os
import json

# Helper functions
def start_processing_video(event, context):
    for record in event["Records"]:
        start_label_detection(
            record["s3"]["bucket"]["name"],
            urllib.parse.unquote_plus(record["s3"]["object"]["key"]),
        )

    return


def get_video_labels(job_id):
    rek_client = boto3.client("rekognition")
    # get the response via the job id
    response = rek_client.get_label_detection(JobId=job_id)
    # rekognition response has a limit of 1000 labels, so we need to determine if there is a "next token"
    # e.g. there is more data
    next_token = response.get("NextToken", None)
    # if there is more data get it and append it to the labels list in the intial response
    while next_token:
        next_page = rek_client.get_label_detection(JobId=job_id, NextToken=next_token)

        next_token = next_page.get("NextToken", None)

        response["Labels"].extend(next_page["Labels"])

    return response


# recursive fn, if item is a dictionary, call function again on that dict. if item is a float, return it as a
# string so it can be stored in dynamoDB (which doesn't accept python floats)
# also have recursion for a list. the response contains nested dicts and lists
def make_item(data):
    if isinstance(data, dict):
        return {k: make_item(v) for k, v in data.items()}
    if isinstance(data, list):
        return [make_item(v) for v in data]
    if isinstance(data, float):
        return str(data)
    else:
        return data


def put_labels_in_db(data, video_name, video_bucket):
    del data["ResponseMetadata"]
    del data["JobStatus"]

    data["videoName"] = video_name
    data["videoBucket"] = video_bucket

    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ["DYNAMODB_TABLE_NAME"]
    videos_table = dynamodb.Table(table_name)

    data = make_item(data)
    videos_table.put_item(Item=data)

    return


# Lambda Events
def start_label_detection(bucket, key):
    rek_client = boto3.client("rekognition")
    response = rek_client.start_label_detection(
        Video={"S3Object": {"Bucket": bucket, "Name": key}},
        NotificationChannel={
            "SNSTopicArn": os.environ["REKOGNITION_SNS_TOPIC_ARN"],
            "RoleArn": os.environ["REKOGNITION_ROLE_ARN"],
        },
    )

    print(response)
    return


def handle_label_detection(event, context):
    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])
        job_id = message["JobId"]
        s3_object = message["Video"]["S3ObjectName"]
        s3_bucket = message["Video"]["S3Bucket"]

        response = get_video_labels(job_id)
        put_labels_in_db(response, s3_object, s3_bucket)

    return

