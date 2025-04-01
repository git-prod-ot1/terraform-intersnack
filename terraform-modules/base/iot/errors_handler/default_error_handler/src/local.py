import os

from dotenv import load_dotenv

load_dotenv(".test.env")
# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE

from main import lambda_handler


class DummyContext:
    def get_remaining_time_in_millis(self):
        return float(os.environ["LAMBDA_TIMEOUT"])


if __name__ == '__main__':
    event = {'Records': [{'messageId': '678b5eb3-2bc2-4c95-a1c7-b269693b69f0',
                          'receiptHandle': 'AQEBCfAz/k3swwoIhPYrkjZl04EhKxeQIL2N3KYYh1FrGAx6YaqaIAs1yQS5G90PLmKj5LdSTjmMXxyGM5tKz9X1PS4hsOVBjgPP2qPbC9xG2N5i3HUpiE0CcSoa85/+hJZsfdWSDmnMm/oVNx0nBXU/lnWGsiD6CTPwsVbhnnMOrX4/PfXUVBAq0x5GmTICYeGa8vhSXxc6f8cY6GHrSibBBK1Za+Bu4EyDgwoHcIyXHyQR87ELngqcz7jBVcoGceJhtT0ZUwYAwDA5BVeL2/6PB0mCAXByWIlSIdTfGFhaDQCe5Cyb06GOAXgyQEV2wbweXp2tpJNNwshkVAskU/Grmv87YEZ0/URZ0DlT+tAp/hoaAupcJrSCZ/HU9V2Z+0kSctxOCWEZnVTbEgzx7/il3YZuNLJ2HjQBMcz6+c3uRLA=',
                          'body': 'eyJydWxlTmFtZSI6ImRldl9zd19pb3RfcmV0cnlfcnVsZSIsInRvcGljIjoiZGV2X3N3X2lvdF9yZXRyeV9kYXRhIiwiY2xvdWR3YXRjaFRyYWNlSWQiOiIyMjg1MDNhYS00OGJlLTI5NWYtOThjMC01M2ZmNjRlNGQxZmUiLCJjbGllbnRJZCI6ImlvdGNvbnNvbGUtYzU3MjQzZTQtNjc5ZC00ZTA0LWFhNGItMDYxZDMzODJlMDBlIiwic291cmNlSXAiOiIxNzguMjM1LjE3Ni4xMDgiLCJiYXNlNjRPcmlnaW5hbFBheWxvYWQiOiJld29nSUNBZ0lDQWdJQ0oyWVd4MVpTSTZJQ0pqYjNKeVpXTjBNU0lzQ2lBZ0lDQWdJQ0FnSW1SaGRHRlFiMmx1ZEVsa0lqb2dJbk52YldWZlpHRjBZWEJ2YVc1MGFXUWlMQW9nSUNBZ0lDQWdJQ0owWVd0bGJrRjBJam9nSWpJd01qRXRNRGd0TWpWVU1EZzZNRFk2TkRBdU16RTJXaUlzQ2lBZ0lDQWdJQ0FnSW5CdmMzUmxaRUYwSWpvZ0lqSXdNakV0TURndE1qVlVNRGc2TURZNk5EQXVNekUyV2lJc0NpQWdJQ0FnSUNBZ0ltTnZibVpwWjNWeVlYUnBiMjVOYjJSbGJGWmxjbk5wYjI0aU9pQWlNQzR4TGpBaUxBb2dJQ0FnSUNBZ0lDSnRiMlJsYkZabGNuTnBiMjRpT2lBaU1DNHhMakFpQ2lBZ0lDQWdJSDA9IiwiYmFzZTY0VHJhbnNwYXJlbnRQcm9wZXJ0aWVzIjoiZXlKbWIzSnRZWFJmYVc1a2FXTmhkRzl5SWpvaVZVNVRVRVZEU1VaSlJVUmZRbGxVUlZNaWZRPT0iLCJmYWlsdXJlcyI6W3siZmFpbGVkQWN0aW9uIjoiS2luZXNpc0FjdGlvbiIsImZhaWxlZFJlc291cmNlIjoiZGV2X3N3X2lvdF9yZXRyeV9kYXRhX3N0cmVhbSIsImVycm9yTWVzc2FnZSI6IkZhaWxlZCB0byBwdWJsaXNoIEtpbmVzaXMgbWVzc2FnZS4gVGhlIGVycm9yIHJlY2VpdmVkIHdhcyBVc2VyOiBhcm46YXdzOnN0czo6MDc2NTY1NDY3MTc1OmFzc3VtZWQtcm9sZS9kZXZfc3dfaW90X3JldHJ5X2lvdC8xZlkzR2JSUCBpcyBub3QgYXV0aG9yaXplZCB0byBwZXJmb3JtOiBraW5lc2lzOlB1dFJlY29yZCBvbiByZXNvdXJjZTogYXJuOmF3czpraW5lc2lzOmV1LWNlbnRyYWwtMTowNzY1NjU0NjcxNzU6c3RyZWFtL2Rldl9zd19pb3RfcmV0cnlfZGF0YV9zdHJlYW0gYmVjYXVzZSBubyBpZGVudGl0eS1iYXNlZCBwb2xpY3kgYWxsb3dzIHRoZSBraW5lc2lzOlB1dFJlY29yZCBhY3Rpb24gKFNlcnZpY2U6IEFtYXpvbktpbmVzaXM7IFN0YXR1cyBDb2RlOiA0MDA7IEVycm9yIENvZGU6IEFjY2Vzc0RlbmllZEV4Y2VwdGlvbjsgUmVxdWVzdCBJRDogY2E2ZWI0ZGMtOGM5My0zN2ViLTk1MmMtY2FkNTczZTNjNTc1OyBQcm94eTogbnVsbCkuIE1lc3NhZ2UgYXJyaXZlZCBvbjogZGV2X3N3X2lvdF9yZXRyeV9kYXRhLCBBY3Rpb246IGtpbmVzaXMsIE5hbWU6IGRldl9zd19pb3RfcmV0cnlfZGF0YV9zdHJlYW0sIFBhcnRpdGlvbktleTogYmI4NjhlODYtYTAzMS00ZWEyLTk5NDEtODFkMzVlYTcwZmQ3In1dfQ==',
                          'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1724414921919',
                                         'SenderId': 'AROARDU5IKATTQA27XVXT:ZBiNlni1',
                                         'ApproximateFirstReceiveTimestamp': '1724414921920'}, 'messageAttributes': {},
                          'md5OfBody': 'ddd13cb35a8b516537d6a2c393b8cc8c', 'eventSource': 'aws:sqs',
                          'eventSourceARN': 'arn:aws:sqs:eu-central-1:076565467175:dev_sw_iot_rules_errors',
                          'awsRegion': 'eu-central-1'}]}
    lambda_handler(event, DummyContext())
