import os
import json
from dotenv import load_dotenv
load_dotenv("./.test.env")

import boto3

from main import handler

class DummyContext:
    def __init__(self):
        self.start = 15 * 1000
        self.aws_request_id = "1111111-1111111"

    def get_remaining_time_in_millis(self):
        self.start -= 1 * 1000
        return self.start


def fetch_single_message_from_sqs(queue_url):
    sqs = boto3.client("sqs")
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=1,
        AttributeNames=["All"],  # Fetch all attributes
        MessageAttributeNames=["All"],  # Fetch custom message attributes
    )
    return response.get("Messages", [None])[0]


if __name__ == "__main__":
    load_dotenv("./.test.env")
    queue_url = os.getenv("QUEUE_URL")

    if not queue_url:
        print("QUEUE_URL is not set in the .test.env file.")
        exit(1)

    message = fetch_single_message_from_sqs(queue_url)

    if not message:
        print("No messages found in the SQS queue.")
        exit(0)

    sqs_event = {
        "Records": [
            {
                "messageId": message["MessageId"],
                "receiptHandle": message["ReceiptHandle"],
                "body": message["Body"],
                "attributes": message.get("Attributes", {}),
                "messageAttributes": message.get("MessageAttributes", {}),
                "md5OfBody": message["MD5OfBody"],
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs",
                "awsRegion": os.getenv("AWS_REGION", "us-east-1"),
            }
        ]
    }

    print("Simulated SQS Event:")
    print(json.dumps(sqs_event, indent=4))

    handler(sqs_event, DummyContext())
