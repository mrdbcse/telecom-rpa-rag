import os
import zipfile

import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = "us-east-1"
PROFILE_NAME = "gen-ai-ops"
session = boto3.Session(profile_name=PROFILE_NAME)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMBDA_FOLDER = os.path.join(BASE_DIR, "lambda")

# print(f"{BASE_DIR=}")
# print(f"{LAMBDA_FOLDER=}")


def list_lambda_folders():
    folders = [
        f
        for f in os.listdir(LAMBDA_FOLDER)
        if os.path.isdir(os.path.join(LAMBDA_FOLDER, f))
    ]

    # print(folders)
    return folders


def zip_lambda_code(folder_name: str) -> str:
    zip_name = f"{folder_name}.zip"
    folder_path = os.path.join(LAMBDA_FOLDER, folder_name)

    app_path = os.path.join(folder_path, "lambda_function.py")

    print(f"Zipping Lambda code: {folder_name}")

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zip_f:
        zip_f.write(app_path, "lambda_function.py")

    print(f"Zip file created successfully: {zip_name}")
    return zip_name


def update_lambda(function_name: str, zip_file: str) -> None:
    client = session.client("lambda", region_name=REGION)

    with open(zip_file, "rb") as f:
        zipped_code = f.read()

    print(f"Updating Lambda: {function_name}")

    response_code = client.update_function_code(
        FunctionName=function_name, ZipFile=zipped_code, Publish=True
    )

    print("Response Code:\n", response_code)

    print(f"{function_name} Code update initiated.")
    print(f"Latest Version: {response_code['Version']}")

    waiter = client.get_waiter("function_updated")
    print(f"Waiting for Lambda {function_name} to finish updating")
    waiter.wait(FunctionName=function_name)

    print(f"Lambda {function_name} update complete")

    if function_name == "start_textract_document_analysis_job":
        response_config = client.update_function_configuration(
            FunctionName=function_name,
            Environment={
                "Variables": {
                    "SNS_TOPIC_ARN_DOCUMENT_ANALYSIS_COMPLETED": os.getenv(
                        "SNS_TOPIC_ARN_DOCUMENT_ANALYSIS_COMPLETED"
                    ),
                    "TEXTRACT_ROLE_ARN": os.getenv("TEXTRACT_ROLE_ARN"),
                }
            },
        )

        print("Environment variables updated.")
        print("Response Configuration:\n", response_config)


def main():
    folders = list_lambda_folders()

    if not folders:
        print("No Lambda folders found")
        return

    print("Available Lambda Functions:")

    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")

    choice = int(input("Enter number to deploy: "))

    if choice < 1 or choice > len(folders):
        print("Invalid Choice.")
        return

    selected_folder = folders[choice - 1]
    zip_file = zip_lambda_code(folder_name=selected_folder)
    update_lambda(function_name=selected_folder, zip_file=zip_file)


if __name__ == "__main__":
    main()
