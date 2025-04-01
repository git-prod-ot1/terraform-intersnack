import os

from dotenv import load_dotenv

load_dotenv("./.test.env")

from main import lambda_handler

class DummyContext:
    aws_request_id = "1111111-1111111"

    def get_remaining_time_in_millis(self):
        return 30000


if __name__ == '__main__':
    my_event = {
        "Records": [
            {
                "kinesis": {
                    "kinesisSchemaVersion": "1.0",
                    "partitionKey": "704cf15f-13da-4b8f-b359-c15bec6657b6",
                    "sequenceNumber": "49622479900524262207957725023793434116151536663568318771",
                    "data": "ewogICAgImRhdGEiOiBbCiAgICAgICAgewogICAgICAgICAgICAiZGF0YXBvaW50aWQiOiAidGVzdDEiLAogICAgICAgICAgICAidmFsdWUiOiA2MTYuNjg1NzI5OTgwNDY5LAogICAgICAgICAgICAidGFrZW5BdCI6ICIyMDIyLTA0LTExVDE2OjMzOjAyLjM5NVoiLAogICAgICAgICAgICAicG9zdGVkQXQiOiAiMjAyMi0wNC0xMVQxNjozMzowMi40NTNaIiwKICAgICAgICAgICAgIm1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsCiAgICAgICAgICAgICJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjogIjAuMS4wIiwKICAgICAgICAgICAgImFkZGl0aW9uYWxkYXRhIjogIndvcmtzQSIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICAgImRhdGFwb2ludGlkIjogInRlc3QyIiwKICAgICAgICAgICAgInZhbHVlIjogNjE2LjY4NTcyOTk4MDQ2OSwKICAgICAgICAgICAgInRha2VuQXQiOiAiMjAyMi0wNC0xMVQxNjozMzowMi4zOTVaIiwKICAgICAgICAgICAgInBvc3RlZEF0IjogIjIwMjItMDQtMTFUMTY6MzM6MDIuNDUzWiIsCiAgICAgICAgICAgICJtb2RlbFZlcnNpb24iOiAiMC4xLjAiLAogICAgICAgICAgICAiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsCiAgICAgICAgICAgICJhZGRpdGlvbmFsZGF0YSI6ICJ3b3Jrc0IiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAgICJkYXRhUG9pbnRJZCI6ICJ0ZXN0MyIsCiAgICAgICAgICAgICJ2YWx1ZSI6IDYxNi42ODU3Mjk5ODA0NjksCiAgICAgICAgICAgICJ0YWtlbkF0IjogIjIwMjItMDQtMTFUMTY6MzM6MDIuMzk1WiIsCiAgICAgICAgICAgICJwb3N0ZWRBdCI6ICIyMDIyLTA0LTExVDE2OjMzOjAyLjQ1M1oiLAogICAgICAgICAgICAibW9kZWxWZXJzaW9uIjogIjAuMS4wIiwKICAgICAgICAgICAgImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiAiMC4xLjAiLAogICAgICAgICAgICAiYWRkaXRpb25hbERhdGEiOiAid29ya3NDIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgICAiZGF0YVBvaW50SWQiOiAidGVzdDQiLAogICAgICAgICAgICAidmFsdWUiOiA2MTYuNjg1NzI5OTgwNDY5LAogICAgICAgICAgICAidGFrZW5BdCI6ICIyMDIyLTA0LTExVDE2OjMzOjAyLjM5NVoiLAogICAgICAgICAgICAicG9zdGVkQXQiOiAiMjAyMi0wNC0xMVQxNjozMzowMi40NTNaIiwKICAgICAgICAgICAgIm1vZGVsVmVyc2lvbiI6ICIwLjEuMCIsCiAgICAgICAgICAgICJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjogIjAuMS4wIiwKICAgICAgICAgICAgImFkZGl0aW9uYWxEYXRhIjogIndvcmtzQyIKICAgICAgICB9CiAgICBdLAogICAgImNsaWVudGlkIjogImRldl9wbGNmX3Rlc3RfMDAwMSIKfQ==",
                    "approximateArrivalTimestamp": 1649694783.991
                },
                "eventSource": "aws:kinesis",
                "eventVersion": "1.0",
                "eventID": "shardId-000000000019:49622479900524262207957725023793434116151536663568318771",
                "eventName": "aws:kinesis:record",
                "invokeIdentityArn": "arn:aws:iam::093961187306:role/dev_plcf_glinojeckSFC_kinesis2timestream_lambda",
                "awsRegion": "eu-central-1",
                "eventSourceARN": "arn:aws:kinesis:eu-central-1:093961187306:stream/dev_plcf_glinojeck_data_stream"
            }
        ]
    }
    lambda_handler(my_event, DummyContext())
