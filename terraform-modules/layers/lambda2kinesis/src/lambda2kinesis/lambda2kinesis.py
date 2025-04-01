import json
import os
import uuid
from typing import List, TypedDict

import boto3

INDEX_BUCKET_NOT_DEFINED = "INDEX_BUCKET_NAME not defined"
MAX_KINESIS_DATA_LENGTH = 20
MAX_FIREHOSE_DATA_LENGTH = 20

UNIT_NAME = None
STAGE = None
COMPANY_NAMESPACE = None
KINESIS_STREAM_NAME = None
FIREHOSE_STREAM_NAME = None
CLIENT_NAME = None
INDEX_BUCKET_NAME = None
DEFAULT_FILE_INDEX_NAME = "LAST_PROCESSED_TIMESTAMP.txt"

firehose = boto3.client('firehose')
kinesis = boto3.client('kinesis')
s3 = boto3.client('s3')


class EnvMissingException(Exception):
	pass


class S3Exception(Exception):
	pass


class TimedRecord(TypedDict):
	takenAt: str


TimedRecords = List[TimedRecord]


def init_default_env():
	global UNIT_NAME, STAGE, \
		COMPANY_NAMESPACE, KINESIS_STREAM_NAME, FIREHOSE_STREAM_NAME, CLIENT_NAME, INDEX_BUCKET_NAME
	UNIT_NAME = os.environ['UNIT_NAME']
	COMPANY_NAMESPACE = os.environ['COMPANY_NAMESPACE']
	KINESIS_STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME') or None
	FIREHOSE_STREAM_NAME = os.environ.get('FIREHOSE_STREAM_NAME') or None
	CLIENT_NAME = os.environ['CLIENT_NAME']
	STAGE = os.environ['STAGE']
	INDEX_BUCKET_NAME = os.environ.get('INDEX_BUCKET_NAME') or None


def send_to_kinesis(records: TimedRecords):
	chunks = _split_into_chunks(records, MAX_KINESIS_DATA_LENGTH)
	for chunk in chunks:
		_send_data_kinesis_chunk(chunk)


def _send_data_kinesis_chunk(records):
	record_aggregated = {
		"data": records,
		"clientid": CLIENT_NAME
	}
	kinesis.put_records(
		Records=[
			{
				'Data': bytes(json.dumps(record_aggregated, ensure_ascii=False), 'utf-8'),
				'PartitionKey': str(uuid.uuid4())
			}
		],
		StreamName=KINESIS_STREAM_NAME
	)


def divide_chunks(l):
	for i in range(0, len(l), MAX_KINESIS_DATA_LENGTH):
		yield l[i:i + MAX_KINESIS_DATA_LENGTH]


def get_last_index(id, index_name=DEFAULT_FILE_INDEX_NAME):
	if INDEX_BUCKET_NAME is None:
		raise EnvMissingException(INDEX_BUCKET_NOT_DEFINED)
	try:
		key = f"data/{UNIT_NAME}/{id}/{index_name}"
		data = s3.get_object(Bucket=INDEX_BUCKET_NAME, Key=key)
		return int(data['Body'].read().decode("UTF-8").strip())
	except s3.exceptions.NoSuchKey as e:
		print(f"No key found in S3 {{id={id}, index_name={index_name}}}")
		return None
	except Exception as e:
		raise S3Exception(
			f"Could not fetch last processing timestamp for id {{id={id}, type={type(e)},  e={str(e)} }}") from e


def store_error(device_id, process_start, error):
	if INDEX_BUCKET_NAME is None:
		raise EnvMissingException(INDEX_BUCKET_NOT_DEFINED)
	s3.put_object(
		Body=str(error),
		Bucket=INDEX_BUCKET_NAME,
		Key=f"errors/{UNIT_NAME}/{device_id}/{process_start}.txt",
		ContentType="text/plain"
	)


def put_last_index(id, content, index_name=DEFAULT_FILE_INDEX_NAME):
	if INDEX_BUCKET_NAME is None:
		raise EnvMissingException(INDEX_BUCKET_NOT_DEFINED)
	s3.put_object(
		Body=str(int(content)),
		Bucket=INDEX_BUCKET_NAME,
		Key=f"data/{UNIT_NAME}/{id}/{index_name}",
		ContentType="text/plain"
	)


def get_secret(secret_name):
	region_name = "eu-central-1"

	# Create a Secrets Manager client
	session = boto3.session.Session()
	client = session.client(
		service_name='secretsmanager',
		region_name=region_name
	)

	try:
		get_secret_value_response = client.get_secret_value(
			SecretId=secret_name
		)
		return json.loads(get_secret_value_response['SecretString'])
	except Exception as e:
		print(f"Could not load secret due to {e}")
		raise e


def send_to_firehose(records: TimedRecords):
	chunks = _split_into_chunks(records, MAX_FIREHOSE_DATA_LENGTH)
	for chunk in chunks:
		_send_data_firehose_chunk(chunk)


def _split_into_chunks(records: TimedRecords, chunk_size: int):
	chunks = []

	grouped_by_date = {}
	for r in records:
		date = r['takenAt'][:10]
		if date in grouped_by_date:
			grouped_by_date[date].append(r)
		else:
			grouped_by_date[date] = [r]

	for date in grouped_by_date.keys():
		chunk = []
		for record in grouped_by_date[date]:
			chunk.append(record)
			if len(chunk) == chunk_size:
				chunks.append(chunk)
				chunk = []
		if chunk:
			chunks.append(chunk)
	return chunks


# send remaining records that are less than MAX_FIREHOSE_DATA_LENGTH
def _send_data_firehose_chunk(records):
	record_aggregated = {
		"data": records,
		"clientid": CLIENT_NAME
	}
	firehose.put_record_batch(
		Records=[{
			'Data': bytes(json.dumps(record_aggregated, ensure_ascii=False), 'utf-8')
		}],
		DeliveryStreamName=FIREHOSE_STREAM_NAME
	)
