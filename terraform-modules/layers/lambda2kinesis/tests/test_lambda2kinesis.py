import json
from unittest.mock import patch

import pytest

from lambda2kinesis.lambda2kinesis import send_to_kinesis, send_to_firehose


@pytest.mark.parametrize('records, send_count', [
	([{"takenAt": "2022-12-12 12:12:12"}], 1),
	([{"takenAt": "2022-12-12 12:12:12"}, {"takenAt": "2022-12-12 17:00:00"}], 1),
	([{"takenAt": "2022-12-12 12:12:12"}, {"takenAt": "2022-12-13 17:00:00"}], 2),
	([{"takenAt": "2022-12-12 12:12:12"}] * 20, 1),
	([{"takenAt": "2022-12-12 12:12:12"}] * 30, 2),
	([{"takenAt": "2022-12-12 12:12:12"}] * 50, 3),
])
@patch('lambda2kinesis.lambda2kinesis.kinesis')
def test_measurements_are_grouped_and_sent_by_takenat_in_kinesis(mock_kinesis, records, send_count):
	# given - parametrized test

	# when - sending to kinesis a list of records
	send_to_kinesis(records)

	# then - records are grouped by date in batches
	assert mock_kinesis.put_records.call_count == send_count
	call_args_list = mock_kinesis.put_records.call_args_list

	# and - the number of sent messages is the same as input messages
	records_count = sum([extract_records_size_from_call_args(call_args) for call_args in call_args_list])
	assert records_count == len(records)


@pytest.mark.parametrize('records, send_count', [
	([{"takenAt": "2022-12-12 12:12:12"}], 1),
	([{"takenAt": "2022-12-12 12:12:12"}, {"takenAt": "2022-12-12 17:00:00"}], 1),
	([{"takenAt": "2022-12-12 12:12:12"}, {"takenAt": "2022-12-13 17:00:00"}], 2),
	([{"takenAt": "2022-12-12 12:12:12"}] * 20, 1),
	([{"takenAt": "2022-12-12 12:12:12"}] * 30, 2),
	([{"takenAt": "2022-12-12 12:12:12"}] * 50, 3),
])
@patch('lambda2kinesis.lambda2kinesis.firehose')
def test_measurements_are_grouped_and_sent_by_takenat_by_firehose(mock_firehose, records, send_count):
	# given - parametrized test

	# when - sending to kinesis a list of records
	send_to_firehose(records)

	# then - records are grouped by date in batches
	assert mock_firehose.put_record_batch.call_count == send_count
	call_args_list = mock_firehose.put_record_batch.call_args_list

	# and - the number of sent messages is the same as input messages
	records_count = sum([extract_records_size_from_call_args(call_args) for call_args in call_args_list])
	assert records_count == len(records)


def extract_records_size_from_call_args(call_args):
	return len(json.loads(call_args.kwargs['Records'][0]['Data'].decode())['data'])
