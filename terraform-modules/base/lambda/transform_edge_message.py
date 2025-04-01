import json
import base64
import boto3
import itertools
import os
import sys
from datetime import datetime
import traceback


s3 = None
CONFIGURATION_BUCKET_NAME = None
CONFIGURATION_FILENAME_PATTERN = None
CONFIGURATION_FILES_CACHE = None


def lambda_handler(event, context):
    """
    Processes sensor measurement samples.
    Trims all whitespaces, verifies there are no blank strings and appends a 'receivedAt' timestamp.
    Attaches a 'context' field containing a list of all tuples with relations to other entities.
    This file needs to be present in S3 conforming to a naming convention defined in
    CONFIGURATION_FILENAME_PATTERN environment variable.
    """

    print(f"Starting Firehose transformation lambda, event = {event}")
    initialize_lambda()

    factory = determine_factory(event)
    output = [transform(record, lambda r: transform_data(r, factory)) for record in event['records']]

    print("Returning output", output)
    return {'records': output}


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


def transform_data(record, factory):
    """
    Factory configuration files fetched from S3 must
    conform to a naming convention provided through CONFIGURATION_FILENAME_PATTERN
    environment variable. The file name must include factory ID and configuration
    model version.
    """

    sample = deserialize_from_base64(record['data'])

    configuration_filename = CONFIGURATION_FILENAME_PATTERN \
        .replace('{factory}', factory) \
        .replace('{modelVersion}', sample['configurationModelVersion'])
    configuration = fetch_configuration(CONFIGURATION_BUCKET_NAME, configuration_filename)

    verify_data_point_exists(sample, configuration)
    merged_with_date = {**sample, "receivedAt": format_date_with_milliseconds(int(record['approximateArrivalTimestamp'])) }

    return serialize_to_base64(merged_with_date)


def initialize_lambda():
    global CONFIGURATION_BUCKET_NAME, CONFIGURATION_FILENAME_PATTERN, CONFIGURATION_FILES_CACHE, s3

    CONFIGURATION_BUCKET_NAME = os.environ['FACTORY_CONFIGURATION_BUCKET_NAME']
    CONFIGURATION_FILENAME_PATTERN = os.environ['FACTORY_CONFIGURATION_FILENAME_PATTERN']
    CONFIGURATION_FILES_CACHE = dict()
    s3 = boto3.client('s3')


def determine_factory(event):
    """
    Determine factory based on Firehose delivery stream name.
    All events not send through Firehose, e.g. those send with Lambda test
    expect to have a configuration called "test", so make sure it's present in S3
    """
    delivery_stream_arn = event["deliveryStreamArn"]
    if delivery_stream_arn.startswith("arn:aws:firehose"):
        return delivery_stream_arn.split('/')[1].split('-')[1]
    else:
        return "test"


def deserialize_from_base64(base64_string):
    decoded = base64.b64decode(base64_string).decode("UTF-8")
    deserialized = json.loads(decoded)
    stripped = strip_object_strings(deserialized)

    return stripped


def serialize_to_base64(some_dict):
    serialized = json.dumps(some_dict, ensure_ascii=False) + '\n'
    encoded = base64.b64encode(serialized.encode("UTF-8")).decode("UTF-8")

    return encoded


def strip_object_strings(obj):
    if isinstance(obj, str):
        stripped = obj.strip()
        if stripped == '':
            raise Exception("Blank strings are not allowed")
        else:
            return stripped
    if isinstance(obj, list):
        return [strip_object_strings(element) for element in obj]
    if isinstance(obj, dict):
        return {k.strip(): strip_object_strings(v) for k, v in obj.items()}
    else:
        return obj


def fetch_configuration(bucket, filename):
    cache_key = f"{bucket}/{filename}"
    try:
        if cache_key in CONFIGURATION_FILES_CACHE:
            print(f"Retrieving factory configuration file from cache, key = '{cache_key}'")
            return CONFIGURATION_FILES_CACHE[cache_key]
        else:
            print(f"Fetching factory configuration file, key = {cache_key}")
            data = s3.get_object(Bucket=bucket, Key=filename)
            content = data['Body'].read().decode("UTF-8").strip()
            parsed = [json.loads(line) for line in content.split('\n')]
            CONFIGURATION_FILES_CACHE[cache_key] = parsed
            return CONFIGURATION_FILES_CACHE[cache_key]
    except Exception as e:
        raise Exception(f"Could not fetch factory configuration file from S3, key = '{cache_key}'") from e


def format_date_with_milliseconds(posix_timestamp_in_milliseconds):
    date_with_6_milli_digits = datetime.utcfromtimestamp(posix_timestamp_in_milliseconds / 1000).strftime('%Y-%m-%dT%H:%M:%S.%f')
    return f"{date_with_6_milli_digits[:-3]}Z"


def verify_data_point_exists(sample, configuration):
    data_point_in_sample = sample["dataPointId"]
    if not any(context["dataPointId"] == data_point_in_sample for context in configuration):
        raise Exception(f"Received data point is not present in factory configuration, dataPointId = {data_point_in_sample}") from e
