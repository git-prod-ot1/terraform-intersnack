import os

import boto3

from message_transformer import MessageTransformer

cloudwatch = boto3.client("cloudwatch")

STAGE = None
COMPANY_NAMESPACE = None
TOPIC_PARTITIONS_FROM_IOT_STR = None


def lambda_handler(event, context):
    """
    Processes sensor measurement samples.
    Trims all whitespaces, verifies there are no blank strings and appends a 'receivedAt' timestamp.
    Messages are stored as-is, without building any relations to factory configuration settings.
    """

    # print(f"Starting Firehose transformation lambda, event = {event}")
    initialize_env()
    data_extracted = map(
        lambda el: {
            "data": el["data"],
            "recordId": el["recordId"],
            "approximateArrivalTimestamp": el["approximateArrivalTimestamp"],
        },
        event["records"],
    )
    transformer = MessageTransformer(
        cloudwatch, COMPANY_NAMESPACE, event["invocationId"], TOPIC_PARTITIONS_FROM_IOT_STR
    )

    output = transformer.transform_encoded_records(data_extracted)
    transformer.send_metrics()

    return {"records": output}


def initialize_env():
    global STAGE, COMPANY_NAMESPACE, TOPIC_PARTITIONS_FROM_IOT_STR
    STAGE = os.environ["STAGE"]
    COMPANY_NAMESPACE = os.environ["COMPANY_NAMESPACE"]
    TOPIC_PARTITIONS_FROM_IOT_STR = os.environ.get("TOPIC_PARTITIONS_FROM_IOT_STR", None)
