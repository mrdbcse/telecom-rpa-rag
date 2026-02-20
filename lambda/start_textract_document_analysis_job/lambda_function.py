import json
import os

import boto3

client = boto3.client("textract")
from dotenv import load_dotenv

load_dotenv()


def lambda_handler(event, context):
    print("Processing Event:\n", json.dumps(event, indent=2))
    s3 = event["Records"][0]["s3"]
    bucket = s3["bucket"]["name"]
    key = s3["object"]["key"]

    print(f"{bucket=}")
    print(f"{key=}")

    SNS_TOPIC_ARN_DOCUMENT_ANALYSIS_COMPLETED = os.getenv(
        "SNS_TOPIC_ARN_DOCUMENT_ANALYSIS_COMPLETED"
    )
    TEXTRACT_ROLE_ARN = os.getenv("TEXTRACT_ROLE_ARN")

    document_location = {"S3Object": {"Bucket": bucket, "Name": key}}
    response = client.start_document_analysis(
        DocumentLocation=document_location,
        FeatureTypes=["TABLES", "FORMS"],
        NotificationChannel={
            "SNSTopicArn": SNS_TOPIC_ARN_DOCUMENT_ANALYSIS_COMPLETED,
            "RoleArn": TEXTRACT_ROLE_ARN,
        },
    )

    print("Textract Response:\n", response)

    event["job_id"] = response["JobId"]
    return event
