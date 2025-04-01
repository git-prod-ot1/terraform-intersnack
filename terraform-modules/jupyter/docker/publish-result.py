#!/usr/bin/env python3
import logging
import os
import boto3

logger = logging.getLogger("s3_publisher")
logging.basicConfig()
logger.setLevel(logging.INFO)

logger.info("Publishing to S3")

TARGET_S3_BUCKET = os.environ["TARGET_S3_BUCKET"]
REPORT_NAME = os.environ["REPORT_NAME"]
REPORT_EXT = os.environ.get('REPORT_EXT') or "pdf"
LOCAL_REPORT_NAME = f"report.{REPORT_EXT}"

report_bytes = None

try:
    input_file = open(LOCAL_REPORT_NAME, "rb")
    report_bytes = input_file.read()
except Exception as e:
    raise Exception(f"Report file not found, make sure you used saved it as {LOCAL_REPORT_NAME}")

my_bucket = TARGET_S3_BUCKET
s3 = boto3.resource('s3')
s3.Bucket(my_bucket).put_object(Key=REPORT_NAME, Body=report_bytes)
