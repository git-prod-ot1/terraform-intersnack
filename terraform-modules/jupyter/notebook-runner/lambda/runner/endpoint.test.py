import os

from dotenv import load_dotenv

load_dotenv(".test.env")
# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE

from main import lambda_handler


class DummyContext:
    def get_remaining_time_in_millis(self):
        return float(os.environ["LAMBDA_TIMEOUT"])


if __name__ == '__main__':
    event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        ],
        "detail": {},
        "time_override": True
    }
    print(lambda_handler(event, DummyContext()))
