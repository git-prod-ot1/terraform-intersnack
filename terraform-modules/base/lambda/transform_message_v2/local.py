import json
import uuid

from dotenv import load_dotenv

load_dotenv("./.test.env")

# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE


from main import lambda_handler


class DummyContext:
    def get_remaining_time_in_millis(self):
        return 30000


# if __name__ == '__main__':
#     with open("input.txt") as f:
#         lines = f.readlines()
#         jsons = [json.loads(line) for line in lines]
#         for _ in jsons:
#             event = {
#                 "invocationId": f"{uuid.uuid4()}",
#                 "records": [{
#                     "data": _["rawData"],
#                     "recordId": f"{uuid.uuid4()}",
#                     "approximateArrivalTimestamp": 0
#                 }]
#             }
#             lambda_handler(event, DummyContext())


if __name__ == '__main__':
    event = {
        "invocationId": "8dd437b9-1d6d-4ee2-8f14-be56a11aaee2",
        "sourceKinesisStreamArn": "arn:aws:kinesis:eu-central-1:596966240641:stream/dev_mixes_messages_data_stream",
        "deliveryStreamArn": "arn:aws:firehose:eu-central-1:596966240641:deliverystream/dev_mixed_messages",
        "region": "eu-central-1",
        "records": [
            {
                "recordId": "49615659390235360198692340333316747709505627667520552962000000",
                "approximateArrivalTimestamp": 1613741931873,
                "data": "eyJkYXRhIjp7InZhbHVlIjp7ImNhdGVnb3J5IjoiUXVhbGl0eSBBc3N1cmFuY2UiLCJjb250ZW50Ijp7ImNvbW1lbnQiOiIiLCJ0eXBlIjoiQ29tbWVudCJ9fSwiZGF0YVBvaW50SWQiOiJwaWN0dXJlRXhwbG9yZXJRYVJlcG9ydCIsInRha2VuQXQiOiIyMDIxLTA4LTI1VDA4OjA2OjQwLjMxNloiLCJwb3N0ZWRBdCI6IjIwMjEtMDgtMjVUMDg6MDY6NDAuMzE2WiIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiZmllbGRJZCI6bnVsbCwiZ2VvTG9jYXRpb24iOiJbNTEuMjczNDU4NjAwLDcuMTUwNDM4OTAwXSJ9LCJjbGllbnRpZCI6InByb2RfcGxjZl9waWN0dXJlX2V4cGxvcmVyXzAwMDEifQ==",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333316747709505627667520552962",
                    "subsequenceNumber": 0,
                    "partitionKey": "da5f2a9b-672d-44ab-8920-3532938e6cf0",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931873
                }
            },
            {
                "recordId": "49615659390235360198692340333317956635325242296695259138000000",
                "approximateArrivalTimestamp": 1613741931875,
                "data": "eyJkYXRhIjpbeyJkYXRhUG9pbnRJZCI6IkFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6ImFzY3MiLCJ0YWtlbkF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjZaIiwicG9zdGVkQXQiOiIyMDIxLTAyLTE5VDEzOjM4OjUxLjI2NloiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCJ9LHsiZGF0YVBvaW50SWQiOiJBZ2dyZWdhdGVkIiwidmFsdWUiOiJBZ2dyZWdhdGVkIG1zZyBuciAxIiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjdaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifSx7ImRhdGFQb2ludElkIjoiQWdncmVnYXRlZCIsInZhbHVlIjoiQWdncmVnYXRlZCBtc2cgbnIgMiIsInRha2VuQXQiOiIyMDIxLTAyLTE5VDEzOjM4OjUxLjI2NloiLCJwb3N0ZWRBdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY4WiIsIm1vZGVsVmVyc2lvbiI6IjAuMS4wIiwiY29uZmlndXJhdGlvbk1vZGVsVmVyc2lvbiI6IjAuMS4wIn0seyJkYXRhUG9pbnRJZCI6IkFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6IkFnZ3JlZ2F0ZWQgbXNnIG5yIDMiLCJ0YWtlbkF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjZaIiwicG9zdGVkQXQiOiIyMDIxLTAyLTE5VDEzOjM4OjUxLjI2OVoiLCJtb2RlbFZlcnNpb24iOiIwLjEuMCIsImNvbmZpZ3VyYXRpb25Nb2RlbFZlcnNpb24iOiIwLjEuMCJ9LHsiZGF0YVBvaW50SWQiOiJBZ2dyZWdhdGVkIiwidmFsdWUiOiJBZ2dyZWdhdGVkIG1zZyBuciA0IiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNzBaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifV0sImNsaWVudGlkIjoiZGV2X3BsY2ZfZ2xpbm9qZWNrXzIifQ==",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333317956635325242296695259138",
                    "subsequenceNumber": 0,
                    "partitionKey": "90c5ee1e-cb80-4b22-89b4-77a078d5fc4c",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931875
                }
            },
            {
                "recordId": "49615659390235360198692340333319165561144856925869965314000000",
                "approximateArrivalTimestamp": 1613741931876,
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTm9uLWFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6Ik5vbi1hZ2dyZWdhdGVkIG1zZyBuciAxIiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjdaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifSwiY2xpZW50aWQiOiJkZXZfZ2xpbm9qZWNrMiJ9",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333319165561144856925869965314",
                    "subsequenceNumber": 0,
                    "partitionKey": "bf4bbc80-d1ef-4504-b156-0c2758d88932",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931876
                }
            },
            {
                "recordId": "49615659390235360198692340333320374486964471486325194754000000",
                "approximateArrivalTimestamp": 1613741931879,
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTm9uLWFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6Ik5vbi1hZ2dyZWdhdGVkIG1zZyBuciAwIiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjZaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifSwiY2xpZW50aWQiOiJkZXZfZ2xpbm9qZWNrMiJ9",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333320374486964471486325194754",
                    "subsequenceNumber": 0,
                    "partitionKey": "ccd76eb8-1b70-4420-b5f0-682cfd226727",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931879
                }
            },
            {
                "recordId": "49615659390235360198692340333321583412784086115499900930000000",
                "approximateArrivalTimestamp": 1613741931890,
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTm9uLWFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6Ik5vbi1hZ2dyZWdhdGVkIG1zZyBuciAyIiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjhaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifSwiY2xpZW50aWQiOiJkZXZfZ2xpbm9qZWNrMiJ9",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333321583412784086115499900930",
                    "subsequenceNumber": 0,
                    "partitionKey": "2cde42c7-8619-42ba-86f3-a3b169f60753",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931890
                }
            },
            {
                "recordId": "49615659390235360198692340333322792338603700813394083842000000",
                "approximateArrivalTimestamp": 1613741931893,
                "data": "eyJkYXRhIjp7ImRhdGFQb2ludElkIjoiTm9uLWFnZ3JlZ2F0ZWQiLCJ2YWx1ZSI6Ik5vbi1hZ2dyZWdhdGVkIG1zZyBuciAzIiwidGFrZW5BdCI6IjIwMjEtMDItMTlUMTM6Mzg6NTEuMjY2WiIsInBvc3RlZEF0IjoiMjAyMS0wMi0xOVQxMzozODo1MS4yNjlaIiwibW9kZWxWZXJzaW9uIjoiMC4xLjAiLCJjb25maWd1cmF0aW9uTW9kZWxWZXJzaW9uIjoiMC4xLjAifSwiY2xpZW50aWQiOiJkZXZfZ2xpbm9qZWNrMiJ9",
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333322792338603700813394083842",
                    "subsequenceNumber": 0,
                    "partitionKey": "251111fb-b8a5-4f16-915b-7d398c34ee2c",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931893
                }
            }
        ]
    }

    lambda_handler(event, None)
