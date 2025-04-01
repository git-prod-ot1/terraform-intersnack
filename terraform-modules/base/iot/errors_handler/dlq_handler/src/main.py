import base64
import json
import logging
import os
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']


def process_message(record):
    try:
        decoded_body = base64.b64decode(record['body']).decode('utf-8')
        body = json.loads(decoded_body)

        topic = body.get('topic', 'unknown')

        logger.info(f"Processing message from topic: {topic}")
        logger.info(f"Message body: {json.dumps(body, indent=2)}")

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        s3_key = f"{topic}/{timestamp}_{record['messageId']}.json"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )

        logger.info(f"Message saved to S3: s3://{S3_BUCKET}/{s3_key}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(f"Original message: {record['body']}")


def lambda_handler(event, context):
    for record in event['Records']:
        process_message(record)
