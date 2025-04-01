import os

from dotenv import load_dotenv

load_dotenv("./.test.env")

from main import lambda_handler

class DummyContext:
    start = 15*1000
    aws_request_id = "1111111-1111111"

    def get_remaining_time_in_millis(self):
        self.start = self.start - 1000
        return self.start


if __name__ == '__main__':
    my_event = {}
    lambda_handler(my_event, DummyContext())
