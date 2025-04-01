import base64
import json
import os
import re
import sys
import traceback
from datetime import datetime

import boto3

cloudwatch = boto3.client('cloudwatch')
client_factory_mapping = {}


def lambda_handler(event, context):
    """
    Processes sensor measurement samples.
    Trims all whitespaces, verifies there are no blank strings and appends a 'receivedAt' timestamp.
    Messages are stored as-is, without building any relations to factory configuration settings.
    """

    # print(f"Starting Firehose transformation lambda, event = {event}")
    initialize_env()
    data_extracted = map(lambda el: {"data": el['data'], "recordId": el["recordId"],
                                     "approximateArrivalTimestamp": el['approximateArrivalTimestamp']},
                         event['records'])
    decoded = list(map(lambda el: {'data': deserialize_from_base64(el['data']), "recordId": el["recordId"],
                                   "approximateArrivalTimestamp": el['approximateArrivalTimestamp']}, data_extracted))

    metrics = {"clients": {}, "factories": {}}
    output = [transform(record, lambda r: transform_data(r, event['invocationId'], metrics)) for record in
              decoded]
    send_client_metrics(metrics["clients"])
    send_factory_metrics(metrics["factories"])

    return {'records': output}


def initialize_env():
    global STAGE, COMPANY_NAMESPACE
    STAGE = os.environ['STAGE']
    COMPANY_NAMESPACE = os.environ['COMPANY_NAMESPACE']

def divide_chunks(l):
    # looping till length l
    for i in range(0, len(l), 20):
        yield l[i:i + 20]


def parse_factory_from_client(client):
    cached_factory = client_factory_mapping.get(client)
    if cached_factory is not None:
        return cached_factory

    match = re.search(f"^(dev_|test_|prod_){COMPANY_NAMESPACE}_(?P<factory>.+)_(0*\\d+)$", client)  # with legacy format handling
    if match is not None:
        factory = match.group("factory")
        client_factory_mapping[client] = factory
        return factory
    else:
        print(f"Could not match factory for metrics: client={client}, make sure client name follows naming "
              f"pattern env_clientName(without _ in it)_clientNumber")
        return None


def send_factory_metrics(metrics_data):
    metrics = []
    for factory, messages_count in metrics_data.items():
        metrics.append({
            'MetricName': 'Messages.Incoming',
            'Dimensions': [
                {
                    'Name': 'Factory',
                    'Value': factory
                }
            ],
            'Unit': 'None',
            'Value': messages_count
        })
    if metrics:
        response = cloudwatch.put_metric_data(
            MetricData=metrics,
            Namespace='IoTCoreCustom'
        )


def send_client_metrics(metrics_data):
    chunked_keys = divide_chunks(list(metrics_data.keys()))
    for group in chunked_keys:
        metrics = []
        for key in group:
            metrics.append({
                'MetricName': 'Messages.Incoming',
                'Dimensions': [
                    {
                        'Name': 'ClientId',
                        'Value': key
                    }
                ],
                'Unit': 'None',
                'Value': metrics_data[key]
            })
        response = cloudwatch.put_metric_data(
            MetricData=metrics,
            Namespace='IoTCoreCustom'
        )


def collect_metrics(client_id, metrics_data, factory_id = None):
    client_metrics = metrics_data["clients"]
    factory_metrics = metrics_data["factories"]

    if client_id in metrics_data["clients"]:
        client_metrics[client_id] += 1
    else:
        client_metrics[client_id] = 1

    factory = factory_id or parse_factory_from_client(client_id)
    if factory is None:
        return

    if factory in metrics_data["factories"]:
        factory_metrics[factory] += 1
    else:
        factory_metrics[factory] = 1


def transform(record, transforming_function):
    try:
        return {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': transforming_function(record)
        }
    except Exception as e:
        print(f"An error occurred while handling a record: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return {
            'recordId': record['recordId'],
            'result': 'ProcessingFailed',
            'data': record['data']
        }


def transform_single(sample, approximate_arrival_timestamp, invocation_id, clientid, metrics_data):
    collect_metrics(clientid, metrics_data, sample.get("factoryid"))
    taken_at = datetime.fromisoformat(sample['takenAt'].replace("Z", "+00:00"))
    posted_at = datetime.fromisoformat(sample['postedAt'].replace("Z", "+00:00"))
    received_at = datetime.utcfromtimestamp(int(approximate_arrival_timestamp) / 1000)
    taken_at_end = datetime.fromisoformat(
        sample['takenAtEnd'].replace("Z", "+00:00")) if "takenAtEnd" in sample else None

    merged_with_additional_fields = {
        **sample,
        "invocationId": invocation_id,
        "receivedAt": transform_date_to_athena_compliant_format(received_at),
        "takenAt": transform_date_to_athena_compliant_format(taken_at),
        "postedAt": transform_date_to_athena_compliant_format(posted_at),
        "takenAtEnd": transform_date_to_athena_compliant_format(taken_at_end),
        "year": str(taken_at.year),
        "month": str(taken_at.month),
        "day": str(taken_at.day),
        "hour": taken_at.strftime("%H")
    }
    return serialize_to_base64(json.dumps(merged_with_additional_fields, ensure_ascii=False))


def transform_list_element(sample, approximate_arrival_timestamp, invocation_id, clientid, metrics_data):
    collect_metrics(clientid, metrics_data, sample.get("factoryid"))
    taken_at = datetime.fromisoformat(sample['takenAt'].replace("Z", "+00:00"))
    posted_at = datetime.fromisoformat(sample['postedAt'].replace("Z", "+00:00"))
    received_at = datetime.utcfromtimestamp(int(approximate_arrival_timestamp) / 1000)
    taken_at_end = datetime.fromisoformat(
        sample['takenAtEnd'].replace("Z", "+00:00")) if "takenAtEnd" in sample else None

    merged_with_additional_fields = {
        **sample,
        "invocationId": invocation_id,
        "receivedAt": transform_date_to_athena_compliant_format(received_at),
        "takenAt": transform_date_to_athena_compliant_format(taken_at),
        "postedAt": transform_date_to_athena_compliant_format(posted_at),
        "takenAtEnd": transform_date_to_athena_compliant_format(taken_at_end),
        "year": str(taken_at.year),
        "month": str(taken_at.month),
        "day": str(taken_at.day),
        "hour": taken_at.strftime("%H")
    }
    return json.dumps(merged_with_additional_fields, ensure_ascii=False)


def transform_list(record, invocation_id, metrics_data):
    result = []
    for el in record['data']['data']:
        result.append(
            transform_list_element(el, record['approximateArrivalTimestamp'], invocation_id, record['data']['clientid'],
                                   metrics_data))
    return serialize_to_base64("".join(result))


def transform_data(record, invocation_id, metrics_data):
    outer_data = record['data']
    if (isinstance(outer_data['data'], list)):
        return transform_list(record, invocation_id, metrics_data)
    else:
        return transform_single(outer_data['data'], record['approximateArrivalTimestamp'], invocation_id,
                                outer_data['clientid'], metrics_data)


def deserialize_from_base64(base64_string):
    decoded = base64.b64decode(base64_string).decode("UTF-8")
    deserialized = json.loads(decoded)
    stripped = strip_object_strings(deserialized)

    return stripped


def serialize_to_base64(json_string):
    encoded = base64.b64encode(json_string.encode("UTF-8")).decode("UTF-8")

    return encoded


def strip_object_strings(obj, key=None):
    if isinstance(obj, str):
        stripped = obj.strip()
        if stripped == '' and key == "value":
            raise Exception("Blank strings are not allowed for value field")
        else:
            return stripped
    if isinstance(obj, list):
        return [strip_object_strings(element) for element in obj]
    if isinstance(obj, dict):
        return {k.strip(): strip_object_strings(v, k) for k, v in obj.items()}
    else:
        return obj


def format_date_with_milliseconds(posix_timestamp_in_milliseconds):
    dt = datetime.utcfromtimestamp(posix_timestamp_in_milliseconds / 1000)
    return transform_date_to_athena_compliant_format(dt)


def transform_date_to_athena_compliant_format(dt):
    if dt is None:
        return None
    date_with_6_milli_digits = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    return f"{date_with_6_milli_digits[:-3]}"


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
