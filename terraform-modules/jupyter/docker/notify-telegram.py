#!/usr/bin/env python3
import json
import logging
import os
import traceback
import boto3
import requests
from botocore.config import Config

logger = logging.getLogger("telegram_notifier")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

logger.info("Notifying Telegram")

try:
    TARGET_S3_BUCKET = os.environ["TARGET_S3_BUCKET"]
    REPORT_NAME = os.environ['REPORT_NAME']
    REPORT_EXT = os.environ.get('REPORT_EXT') or "pdf"

    TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    PROCESS_START = os.environ['PROCESS_START']
    ACTIVITY_TITLE = os.environ.get('ACTIVITY_TITLE') or ''

    credentials = json.loads(os.environ.get('ACCESS_KEY_SECRET'))

    s3 = boto3.client('s3',
                      aws_access_key_id=credentials['access_key'],
                      aws_secret_access_key=credentials['access_key_secret'],
                      config=Config(signature_version='s3v4'))

    response = s3.generate_presigned_url('get_object',
                                         Params={'Bucket': TARGET_S3_BUCKET,
                                                 'Key': REPORT_NAME},
                                         ExpiresIn=3600 * 24 * 7)

    body = {
        "chat_id": int(TELEGRAM_CHAT_ID),
        "parse_mode": "HTML",
        "text": f"{ACTIVITY_TITLE}: <a href=\"{response}\">Link</a>",
    }

    res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=body)
    logger.debug(res.json())
    if not res.ok:
        logger.error(f"Could not post to telegram channel {{res = {res.json()}}}")
except Exception as e:
    logger.error(f"An error occurred while notifying telegram: {str(e)}")
    traceback.print_exc()
