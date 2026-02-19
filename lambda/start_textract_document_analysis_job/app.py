import boto3
import os
import json

client = boto3.client("textract")


def lambda_handler(event, context):
    print("Processing Event:\n", json.dumps(event, indent=2))
    s3 = event["Records"][0]["s3"]
    bucket = s3["bucket"]["name"]
    key = s3["object"]["key"]

    print(f"{bucket=}")
    print(f"{key=}")

    document_location = {"S3Object": {"Bucket": bucket, "Name": key}}
    response = client.start_document_analysis(
        DocumentLocation=document_location, FeatureTypes=["TABLES", "FORMS"]
    )
    return event
