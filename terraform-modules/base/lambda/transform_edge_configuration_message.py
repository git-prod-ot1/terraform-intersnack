import json
import base64
import sys
from datetime import datetime
import traceback


def lambda_handler(event, context):
    """
    Processes factory configuration update message.
    Trims all whitespaces, verifies there are no blank strings and appends a 'receivedAt' timestamp
    """

    print(f"Starting Firehose transformation lambda, event = {event}")

    output = [transform(record, lambda r: transform_data(r)) for record in event['records']]

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


def transform_data(record):
    configuration = deserialize_from_base64(record['data'])
    merged_with_date = {**configuration, "receivedAt": format_date_with_milliseconds(int(record['approximateArrivalTimestamp']))}

    return serialize_to_base64(merged_with_date)


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


def format_date_with_milliseconds(posix_timestamp_in_milliseconds):
    date_with_6_milli_digits = datetime.utcfromtimestamp(posix_timestamp_in_milliseconds / 1000).strftime('%Y-%m-%dT%H:%M:%S.%f')
    return f"{date_with_6_milli_digits[:-3]}Z"
