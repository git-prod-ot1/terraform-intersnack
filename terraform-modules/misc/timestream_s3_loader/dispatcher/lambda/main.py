import json
import logging
import os
import traceback
import time
import hashlib
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Dict, List

import boto3

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

INDEX_BUCKET_NAME: str = os.environ["INDEX_BUCKET_NAME"]
DATA_BUCKET_NAME: str = os.environ["DATA_BUCKET_NAME"]
QUEUE_URL: str = os.environ["QUEUE_URL"]
FACTORY: str = os.environ["FACTORY"]
DATA_PREFIX: str = os.getenv("DATA_PREFIX", f"data/factory={FACTORY}")
INDEX_FILE_KEY: str = "index/last_processed_state.json"
RETENTION_IN_DAYS: int = abs(int(os.getenv("RETENTION_IN_DAYS", 180)) - 1)
ABANDON_TIME_BUFFER_SECONDS: int = 5
BATCH_SIZE: int = 10  # SQS SendMessageBatch allows up to 10 messages per batch

index: Dict[str, Optional[str | date]] = {'last_date': None, 'last_key': None}

def lambda_handler(event, context) -> None:
    try:
        main(context)
    except Exception as e:
        logger.critical(f"Unexpected error happened {{e={e}}}")
        traceback.print_exc()
    finally:
        update_index()

def main(context) -> None:
    global index
    now: datetime = datetime.now(tz=timezone.utc)

    index_data: Optional[Dict[str, Optional[str]]] = get_index()
    if not index_data:
        start_date: date = (now - timedelta(days=RETENTION_IN_DAYS)).date()
        index['last_date'] = start_date
        index['last_key'] = None
    else:
        index['last_date'] = datetime.strptime(index_data['last_date'], "%Y-%m-%d").date()
        index['last_key'] = index_data['last_key']
        logger.info(f"Starting {{start_date={index['last_date']}, last_key={index['last_key']}}}")

    while index['last_date'] <= now.date():
        remaining_time: float = context.get_remaining_time_in_millis() / 1000
        if remaining_time < ABANDON_TIME_BUFFER_SECONDS:
            logger.warning(f"Abandoning processing due to low remaining time: {remaining_time}s.")
            break

        last_key: Optional[str] = process_date(index['last_date'], index['last_key'], context)

        if last_key is None:
            index['last_date'] += timedelta(days=1)
            index['last_key'] = None
        else:
            index['last_key'] = last_key
        logger.info(f"Starting {{start_date={index['last_date']}, last_key={index['last_key']}}}")

def get_index() -> Optional[Dict[str, Optional[str]]]:
    try:
        response = s3.get_object(Bucket=INDEX_BUCKET_NAME, Key=INDEX_FILE_KEY)
        return json.loads(response['Body'].read())
    except s3.exceptions.NoSuchKey:
        return None

def update_index() -> None:
    global index
    if index['last_date'] is not None:
        last_date_str = index['last_date'].strftime("%Y-%m-%d")
    else:
        last_date_str = None

    s3.put_object(
        Bucket=INDEX_BUCKET_NAME,
        Key=INDEX_FILE_KEY,
        Body=json.dumps({
            'last_date': last_date_str,
            'last_key': index['last_key']
        }),
        ContentType="application/json"
    )

def process_date(d: date, last_key: Optional[str], context) -> Optional[str]:
    global index
    prefix: str = f"{DATA_PREFIX}/year={d.year}/month={d.month:02d}/day={d.day:02d}/"
    key_generator = list_keys_with_prefix(DATA_BUCKET_NAME, prefix, last_key)

    batch_messages: List[Dict[str, str]] = []
    last_successful_key: Optional[str] = last_key
    all_processed = True

    for key in key_generator:
        remaining_time: float = context.get_remaining_time_in_millis() / 1000
        if remaining_time < ABANDON_TIME_BUFFER_SECONDS:
            logger.warning(f"Abandoning processing for {d}. Remaining time: {remaining_time}s.")
            all_processed = False
            break

        try:
            message_id = generate_message_id(key)
            message = {
                'Id': message_id,
                'MessageBody': json.dumps({'s3_key': key, 'bucket_name': DATA_BUCKET_NAME})
            }
            batch_messages.append(message)
            last_successful_key = key

            if len(batch_messages) == BATCH_SIZE:
                send_sqs_batch(batch_messages)
                batch_messages.clear()
                index['last_key'] = last_successful_key
        except Exception as e:
            logger.error(f"Failed to queue key {key}. Error: {e}")
            all_processed = False
            break

    if batch_messages:
        try:
            send_sqs_batch(batch_messages)
            index['last_key'] = last_successful_key
            batch_messages.clear()
        except Exception as e:
            logger.error(f"Failed to send final batch for date {d}. Error: {e}")
            all_processed = False

    return None if all_processed else last_successful_key

def list_keys_with_prefix(bucket: str, prefix: str, start_after: Optional[str] = None):
    paginator = s3.get_paginator('list_objects_v2')
    pagination_args = {'Bucket': bucket, 'Prefix': prefix}
    if start_after:
        pagination_args['StartAfter'] = start_after

    for page in paginator.paginate(**pagination_args):
        if 'Contents' in page:
            for obj in page['Contents']:
                if start_after and obj['Key'] <= start_after:
                    continue
                yield obj['Key']

def send_sqs_batch(messages: List[Dict[str, str]]) -> None:
    max_retries = 3
    id_to_message = {msg['Id']: msg for msg in messages}
    for attempt in range(max_retries):
        try:
            response = sqs.send_message_batch(
                QueueUrl=QUEUE_URL,
                Entries=messages
            )
            failed = response.get('Failed', [])
            if not failed:
                return
            messages = [id_to_message[fail['Id']] for fail in failed]
            logger.warning(f"{len(failed)} messages failed to send in attempt {attempt + 1}. Retrying...")
        except Exception as e:
            logger.error(f"Error sending SQS batch on attempt {attempt + 1}: {e}")
        backoff_time = 2 ** attempt
        time.sleep(backoff_time)
    logger.critical(f"Failed to send batch after {max_retries} attempts. Messages: {messages}")
    raise RuntimeError("Failed to send SQS batch after multiple retries.")

def generate_message_id(s3_key: str) -> str:
    """
    Generates a unique, short ID for SQS messages based on the S3 key.
    Uses SHA-256 hash and takes the first 40 characters for uniqueness.
    """
    hash_object = hashlib.sha256(s3_key.encode('utf-8'))
    return hash_object.hexdigest()[:40]
