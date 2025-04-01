import base64
import json
import uuid

import boto3

s3 = boto3.client("s3")
kinesis = boto3.client("kinesis")

# todo: parse from object link
SOURCE_BUCKET = "dev-plcf-ayyeka-measurement-samples"

# TAKES PRECEDENCE!!!
PREFIX_TO_REPROCESS = "errors/factory=ayyeka/processing-failed/year=2022/month=05/day=22/dev_plcf_ayyeka_delivery_stream-2-2022-05-22-17-46-09-32bbf8be-778a-3a2a-bd79-3fb7136090ec"

KINESIS_STREAM_NAME = "dev_plcf_ayyeka_data_stream"


def lambda_handler(event, context):
    for k in get_file_keys_from_prefix(SOURCE_BUCKET, PREFIX_TO_REPROCESS):
        reprocess_single(SOURCE_BUCKET, k)


def reprocess_single(bucket, file_key):
    file = s3.get_object(Bucket=bucket, Key=file_key)['Body'].read()
    data = file \
        .decode('utf-8') \
        .split("\u000a")

    without_empty = [r for r in data if r]
    mapped_json = [json.loads(r) for r in without_empty]
    decoded = [
        json.loads(
            base64.b64decode(r["rawData"])
                .decode('utf-8')
        ) for r in mapped_json]
    for r in decoded:
        reprocess_kinesis(r)
    s3.put_object(Bucket=bucket, Key=f"{file_key}-reprocessed", Body=file)


def get_file_keys_from_prefix(bucket, prefix):
    s3_objects = s3.list_objects(Bucket=bucket, Prefix=prefix)['Contents']
    return [r['Key'] for r in s3_objects if not r['Key'].endswith("-reprocessed")]


def reprocess_kinesis(data):
    return
    print(f"Sending {data}")
    record_aggregated = {
        "data": data['data'],
        "clientid": data['clientid']
    }

    res = kinesis.put_records(
        Records=[
            {
                'Data': bytes(json.dumps(record_aggregated, ensure_ascii=False), 'utf-8'),
                'PartitionKey': str(uuid.uuid4())
            }
        ],
        StreamName=KINESIS_STREAM_NAME
    )
    print(res)


if __name__ == '__main__':
    lambda_handler({}, {})
