import json
import time
from urllib.parse import unquote

import boto3
import os
import uuid
import bson
from bson import InvalidBSON

s3 = boto3.client('s3')
kinesis = boto3.client('kinesis')
my_lambda = boto3.client('lambda')

MINIMUM_REMAINING_TIME_MS = 50 * 1000
READ_BUFFER_SIZE = 524288


def lambda_handler(event, context):
    """
    Parse bson measurements dumps on s3 event sending not null values to kinesis stream.
    Can use custom or none client id as env var CLIENT_ID.
    Current implementation expects bson dumps as: /bsondumps/factory=XXX/dump.bson
    It will use factory parameter from path and env vars: STAGE and COMPANY_NAMESPACE
    to form kinesis stream name: {STAGE}_{COMPANY_NAMESPACE}_{XXX}_data_stream.
    """
    print(f"Starting s3 bsondumps to iot lambda on event = {event}")
    if len(event['Records']) != 1:
        print('Error length of records is not 1')

    initialize_lambda()
    client_id = os.environ.get('CLIENT_ID', None)
    s3_event = event['Records'][0]['s3']
    offset = event['Records'][0].get('bson_processor', {}).get('offset') or 0
    file_size = event['Records'][0]['s3']['object']['size']
    factory = event['Records'][0]['s3']['object']['key'].split('/', 3)[1].split('%3D')[1]
    file_name = event['Records'][0]['s3']['object']['key'].split('/')[-1]
    kinesis_stream_name = '{stage}_plcf_{factory}_data_stream'.format(
        stage=os.environ['STAGE'], namespace={os.environ['COMPANY_NAMESPACE']}, factory=factory)

    print(f"file name = {file_name} ({offset}/{file_size}) client id = {client_id} "
          f"factory = {factory} kinesis stream = {kinesis_stream_name}")

    while offset < file_size and is_there_time_left(context):
        s3_data = read_s3_data(offset, s3_event)
        measurements = []
        data_iterator = bson.decode_iter(s3_data)

        offset = offset + parse_measurements(data_iterator, measurements)
        measurements_count = len(measurements)

        chunked_measurements = divide_chunks(measurements, 20)
        start_sending_time = time.time()
        send_measurements(chunked_measurements, kinesis_stream_name, client_id)
        if measurements_count > 0:
            print(f"Send {measurements_count / 20} records in {time.time() - start_sending_time}s ")

    if offset < file_size:
        reinvoke_lambda(offset, s3_event)


def reinvoke_lambda(offset, s3_event):
    invoke_event = {
        "Records": [
            {
                "description": "Lambda relaunch event to continue processing samples",
                "eventSource": "bson_processor",
                "bson_processor": {
                    "offset": offset
                },
                "s3": s3_event
            }
        ]
    }
    my_lambda.invoke(
        FunctionName='dev_plcf_glinojeck_bsondumptoiot',
        InvocationType='Event',
        Payload=json.dumps(invoke_event)
    )


def send_measurements(chunked_measurements, kinesis_stream_name, client_id):
    for chunk in chunked_measurements:
        kinesis_put_record = create_kinesis_record(chunk, client_id)
        response = kinesis.put_records(
            Records=kinesis_put_record,
            StreamName=kinesis_stream_name
        )
        if response['FailedRecordCount'] != 0:
            print(f"Error kinesis put FailedRecordCount <> 0 response = {response}")
        time.sleep(0.15)


def create_kinesis_record(chunk, client_id):
    data = None
    if client_id is None or client_id == '':
        data = {
            "data": chunk
        }
    else:
        data = {
            "data": chunk,
            "clientid": client_id
        }
    return [
        {
            'Data': bytes(json.dumps(data, ensure_ascii=False), 'utf-8'),
            'PartitionKey': str(uuid.uuid4())
        }
    ]


def parse_measurements(data_iterator, measurements):
    parsed_length = 0
    number_of_samples = 0
    try:
        for measurement in data_iterator:
            parsed_length = parsed_length + len(bson.encode(measurement))
            number_of_samples = number_of_samples + 1
            if measurement['value'] is not None:
                del measurement['_id']  # remove MongoDB id
                measurements.append(measurement)
            if number_of_samples >= 1000:
                # end parsing on 1000th sample as bson parser tends to trip
                break
    except InvalidBSON as e:
        print(f"Error InvalidBSON on parsed_length = {parsed_length}, e = {e}")
    except Exception as e:
        print(f"Error: Exception on parsed_length = {parsed_length}, e = {e}")
    except:
        print(f"Error: on parsed_length = {parsed_length}")
    return parsed_length


def read_s3_data(offset, s3_event):
    return s3.get_object(
        Bucket=s3_event['bucket']['name'],
        Key=unquote(s3_event['object']['key']),
        Range='bytes={}-{}'.format(offset, offset + READ_BUFFER_SIZE - 1)
    )['Body'].read()


def initialize_lambda():
    global s3, my_lambda, kinesis


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def is_there_time_left(context):
    millis_left = context.get_remaining_time_in_millis()
    return millis_left >= MINIMUM_REMAINING_TIME_MS


class Context:
    def __init__(self):
        self.start_millis = round(time.time() * 1000)

    def get_remaining_time_in_millis(self):
        max_processing_millis = int(180 * 1000)
        return max_processing_millis - (round(time.time() * 1000) - self.start_millis)


if __name__ == '__main__':
    test_event_new = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "test"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE12345test",
                    "x-amz-id-2": "EXAMPLE123/test"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "test",
                    "bucket": {
                        "name": "dev-plcf-mongodb",
                        "ownerIdentity": {
                            "principalId": "test"
                        },
                        "arn": "test"
                    },
                    "object": {
                        "key": "bsondumps/factory%3Dglinojecknirs/flows_boilers.bson",
                        "size": 847222131,
                        "eTag": "test",
                        "sequencer": "test"
                    }
                }
            }
        ]
    }
    test_event_continue = {
        "Records": [
            {
                "description": "Lambda relaunch event to continue processing samples",
                "eventSource": "bson_processor",
                "bson_processor": {
                    "offset": 10485396
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "test",
                    "bucket": {
                        "name": "dev-gltest2-measurement-samples",
                        "ownerIdentity": {
                            "principalId": "test"
                        },
                        "arn": "test"
                    },
                    "object": {
                        "key": "bsondumps/factory%3Dglinojecknirs/flows_boilers.bson",
                        "size": 847222131,
                        "eTag": "test",
                        "sequencer": "test"
                    }
                }
            }
        ]
    }
    lambda_handler(test_event_new, Context())
