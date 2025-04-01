import time
import boto3
import gzip
import shutil

s3 = boto3.client('s3')


def lambda_handler(event, context):
    print(f"Starting unpack lambda on event: {event}")
    bucket = event.get('s3')
    archive_s3_key = event.get('archive_key')
    file_s3_key = event.get('output_key')

    archive_file = '/tmp/archive.gz'
    file = '/tmp/archive.bson'

    time_marker = time.time()
    s3.download_file(bucket, archive_s3_key, archive_file)
    print(f"Download time: {time.time() - time_marker}s ")

    time_marker = time.time()
    with gzip.open(archive_file, 'rb') as f_in:
        with open(file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Unpacking time: {time.time() - time_marker}s ")

    time_marker = time.time()
    s3.upload_file(file, bucket, file_s3_key)
    print(f"Uploading time: {time.time() - time_marker}s ")


if __name__ == '__main__':
    test_event = {
        "s3": "dev-plcf-mongodb",
        "archive_key": "GL3_tags_backup/20220226_flows_tec5_4.bson.gz",
        "output_key": "unpacktest/20220226_flows_tec5_4.bson"
    }
    lambda_handler(test_event, None)
