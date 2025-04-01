#!/usr/bin/env python3
import json
import logging
import os
import traceback
import boto3
import requests
from botocore.config import Config

logger = logging.getLogger("teams_notifier")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

logger.info("Notifying Teams")

TARGET_S3_BUCKET = os.environ["TARGET_S3_BUCKET"]
TEAMS_WEBHOOK_URL = os.environ['TEAMS_WEBHOOK_URL']
REPORT_NAME = os.environ['REPORT_NAME']
REPORT_EXT = os.environ.get('REPORT_EXT') or "pdf"
TEAMS_ACTIVITY_TITLE = os.environ.get('TEAMS_ACTIVITY_TITLE') or ''
TEAMS_ACTIVITY_SUBTITLE = os.environ.get('TEAMS_ACTIVITY_SUBTITLE') or ''
TEAMS_ACTIVITY_IMAGE = os.environ.get('TEAMS_ACTIVITY_IMAGE') or ''

ADDITIONAL_MESSAGE_PATH = 'additional_message.txt'

credentials = json.loads(os.environ.get('ACCESS_KEY_SECRET'))

s3 = boto3.client('s3',
                  aws_access_key_id=credentials['access_key'],
                  aws_secret_access_key=credentials['access_key_secret'],
                  config=Config(signature_version='s3v4'))

response = s3.generate_presigned_url('get_object',
                                     Params={'Bucket': TARGET_S3_BUCKET,
                                             'Key': REPORT_NAME},
                                     ExpiresIn=3600 * 24 * 7)

additional_message = ''
if os.path.exists(ADDITIONAL_MESSAGE_PATH):
    with open(ADDITIONAL_MESSAGE_PATH, 'r') as file:
        additional_message = file.read()

body = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "0076D7",
    "summary": f"{TEAMS_ACTIVITY_TITLE}",
    "sections": [{
        "activityTitle": f"{TEAMS_ACTIVITY_TITLE}",
        "activitySubtitle": f"{TEAMS_ACTIVITY_SUBTITLE}",
        "activityImage": f"{TEAMS_ACTIVITY_IMAGE}",
        "facts": [{
            "name": "",
            "value": f"[Report Link]({response}) {additional_message}"
        }],
        "markdown": "true"
    }],
}

try:
    teams_call_result = requests.post(TEAMS_WEBHOOK_URL, json=body)
    logger.debug(f"Teams call result: {teams_call_result.status_code} - {teams_call_result.text}")
    if not teams_call_result.ok:
        logger.error(f"Could not post to teams channel {{res = {teams_call_result.json()}}}")

except Exception as e:
    print(f"An error occurred while notifying teams: {str(e)}")
    traceback.print_exc()
