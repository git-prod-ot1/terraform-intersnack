import json
import os
from dotenv import load_dotenv

load_dotenv(".test.env")
# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE

from main import lambda_handler


class DummyContext:
    def get_remaining_time_in_millis(self):
        return float(os.environ["LAMBDA_TIMEOUT"])


if __name__ == '__main__':
    with open("test_input.json") as f:
        event = json.load(f)
    print(lambda_handler(event, DummyContext()))
