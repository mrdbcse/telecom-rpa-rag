import json


def lambda_handler(event, context):
    print("Processing Event:\n", json.dumps(event, indent=2))
    return {"statusCode": 200, "body": json.dumps("Process Scanned Invoices")}
