import base64
import json
import logging
import os
import re
from datetime import datetime

import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import boto3

from case_insensitive_dict import CaseInsensitiveDict

logger = logging.getLogger("iot_republisher")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

DATAPOINT_ID_PLACEHOLDER = "${datapointid}"
RANGE = 20

TOPIC = None

REFERENCE_TABLES_BUCKET = None
REFERENCE_TABLE_TTL = 240 * 1000  # in ms

s3 = boto3.client("s3")
iot = boto3.client('iot', region_name=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"))
endpoint = os.environ.get("IOT_ENDPOINT") or iot.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress']
reference_table = {"read_at": 1, "content": {}}


def lambda_handler(event, context):
    init_env()

    try:
        refresh_reference_table()
        measurements = get_measurements_from_kinesis_data(event)
        republish_measurements = [m for m in measurements if should_republish(m)]

        start = datetime.utcnow()
        republish(create_iot_client(create_id(context)), republish_measurements)
        print(
            f"It took {datetime.utcnow() - start} to process {len(measurements)} measurements"
        )
    except Exception as e:
        logger.error(f"Something went wrong {e}")


def get_measurements_from_kinesis_data(event):
    records = event["Records"]
    decoded = [decode_record(r) for r in records]
    return flat_map(decoded)


def create_id(context):
    return context.aws_request_id.split("-")[0]


def republish(iot_client, measurements):
    iot_client.connect()

    for m in measurements:
        try:
            topic = create_republish_topic(m)
            result = iot_client.publish(topic, json.dumps(transform(m)), QoS=0)
            if not result:
                logger.error(f"Publishing message failed for={m} on topic={topic}")
        except Exception as e:
            logger.error(f"Could not republish message, {e}")

    iot_client.disconnect()


def create_iot_client(random_postfix):
    client_id = f'{os.environ["STAGE"]}_{os.environ["COMPANY_NAMESPACE"]}_republishlambda_{random_postfix}'

    iot_client = AWSIoTPyMQTT.AWSIoTMQTTClient(client_id, useWebsocket=True)
    iot_client.configureEndpoint(endpoint, 443)
    iot_client.configureCredentials("aws_root.pem")
    return iot_client


def create_republish_topic(m):
    datapoint_id = extract_datapoint_id(m)
    topic = (reference_table["content"].get(datapoint_id) or {}).get(
        "topic"
    ) or reference_table["content"]["defaultTopic"]
    topic = replace_variable_placeholders(topic, CaseInsensitiveDict(m))
    return topic


def extract_datapoint_id(m):
    return m.get("dataPointId") or m.get("datapointid") or None


def transform(m):
    """
    This method transforms a given measurement according to configuration from reference table.
    "example": {
        "republish": true,
        "transformation": {
            "dataPointId": "${dataPointId}_new",
            "additionalData": "${additionalData}_${datapointid}"
        }
    }

    Where values in ${} are original values from given measurement.
    An example result of this transformation is:
    {"dataPointId": "example", "additionalData": "123", "otherValue": "0"}
    into
    {"dataPointId": "example_new", "additionalData": "123_example", "otherValue": "0"}
    """

    transformation = get_transformation_setting(m)
    if not transformation:
        return m

    case_insensitive_m = CaseInsensitiveDict(m)
    result = m.copy()

    for transform_key in transformation:
        result[transform_key] = replace_variable_placeholders(
            transformation[transform_key], case_insensitive_m
        )

    return result


def replace_variable_placeholders(string_value, placeholder_values):
    result = str(string_value)
    for matched_placeholder in re.findall(r"\$\{\w*}", result, re.IGNORECASE):
        variable_name = matched_placeholder[2:-1]  # cut ${} var brackets
        variable_value = placeholder_values.get(variable_name)
        if not variable_value:
            logger.error(
                f"Error during transformation. Measurement does not contain {variable_name}"
            )
            continue
        result = result.replace(matched_placeholder, variable_value)
    return result


def get_transformation_setting(measurement):
    republish_setting = reference_table.get("content", {}).get(
        extract_datapoint_id(measurement), {}
    )
    return republish_setting.get("transformation")


def refresh_reference_table():
    now = int(round(datetime.utcnow().timestamp() * 1000))
    if now - reference_table["read_at"] > REFERENCE_TABLE_TTL:
        logger.info("Refreshing reference table")
        try:
            reference_table_obj = s3.get_object(
                Bucket=REFERENCE_TABLES_BUCKET, Key=f"{UNIT_NAME}.json"
            )
            reference_table["content"] = json.loads(
                reference_table_obj["Body"].read().decode("UTF-8")
            )
            reference_table["read_at"] = now
        except Exception as e:
            logger.error(f"Could not refresh reference_table, e={e}")


def decode_record(record):
    record = base64.b64decode(record["kinesis"]["data"])
    record = json.loads(record).get(
        "data", {"dataPointId": "empty:record", "timestream": False}
    )
    if type(record) is dict:
        record = [record]
    return record


def should_republish(message):
    datapoint_id = extract_datapoint_id(message)
    if datapoint_id is None:
        return False

    return (
      reference_table["content"].get("republish_all")
      or (reference_table["content"].get(datapoint_id) or {}).get("republish")
      or False
    )


def init_env():
    global STAGE, UNIT_NAME, REFERENCE_TABLES_BUCKET

    STAGE = os.environ["STAGE"]
    UNIT_NAME = os.environ["UNIT_NAME"]
    REFERENCE_TABLES_BUCKET = os.environ["REFERENCE_TABLES_BUCKET"]


def flat_map(xs):
    ys = []
    for x in xs:
        ys.extend(x)
    return ys
