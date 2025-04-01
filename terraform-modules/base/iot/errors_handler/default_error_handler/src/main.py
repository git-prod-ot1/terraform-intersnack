import base64
import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')
kinesis = boto3.client('kinesis')

DLQ_URL = None


def init_env():
    logger.info("Initializing environment variables")
    global DLQ_URL
    DLQ_URL = os.environ['DLQ_URL']


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))  # just a temporary log to not lose data
    init_env()
    batch_item_failures = []
    sqs_batch_response = {}

    for record in event['Records']:
        try:
            message_body = json.loads(base64.b64decode(record['body']).decode("utf-8"))

            kinesis_info = get_kinesis_info(message_body)
            if kinesis_info:
                process_kinesis_message(message_body, kinesis_info)
                logger.info(f"Successfully processed Kinesis message: {message_body}")
            else:
                logger.info(f"Non-Kinesis message received, sending to DLQ: {message_body}")
                send_to_dlq(message_body)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            batch_item_failures.append({"itemIdentifier": record['messageId']})

    sqs_batch_response['batchItemFailures'] = batch_item_failures
    return sqs_batch_response


def get_kinesis_info(message_body):
    failures = message_body.get('failures', [])
    for failure in failures:
        if failure.get('failedAction') == 'KinesisAction':
            return {
                'stream_name': failure.get('failedResource'),
                'partition_key': failure.get('partitionKey', 'default'),
                'client_id': message_body.get('clientId')
            }
    return None


def process_kinesis_message(message_body, kinesis_info):
    try:
        original_payload = json.loads(base64.b64decode(message_body.get('base64OriginalPayload', '')).decode('utf-8'))

        new_message = {
            "data": original_payload,
            "clientid": kinesis_info['client_id']
        }
        kinesis.put_record(
            StreamName=kinesis_info['stream_name'],
            Data=json.dumps(new_message).encode('utf-8'),
            PartitionKey=kinesis_info['partition_key']
        )

        logger.info(f"Successfully sent message to Kinesis: {new_message}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing Kinesis message: {str(e)}")
        raise


def send_to_dlq(message):
    sqs.send_message(
        QueueUrl=DLQ_URL,
        MessageBody=json.dumps(message)
    )
