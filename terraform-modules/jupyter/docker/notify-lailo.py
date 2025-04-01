#!/usr/bin/env python3
import json
import logging
import os
import traceback
import boto3
import requests
from botocore.config import Config

logger = logging.getLogger("lailo_notifier")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

logger.info("Notifying Lailo")

TARGET_S3_BUCKET = os.environ["TARGET_S3_BUCKET"]
REPORT_NAME = os.environ['REPORT_NAME']
REPORT_EXT = os.environ.get('REPORT_EXT') or "pdf"
LAILO_WEBHOOK_URL = os.environ['LAILO_WEBHOOK_URL']
PROCESS_START = os.environ['PROCESS_START']
LAILO_ACTIVITY_TITLE = os.environ.get('LAILO_ACTIVITY_TITLE') or ''

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
    "url": response,
    "description": LAILO_ACTIVITY_TITLE,
    "creationDate": PROCESS_START,
}

try:
    requests.post(LAILO_WEBHOOK_URL, json=body)
except Exception as e:
    print(f"An error occurred while notifying lailo: {str(e)}")
    traceback.print_exc()
