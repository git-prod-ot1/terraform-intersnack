from importlib import reload
from unittest.mock import patch, MagicMock
import pytest
from dotenv import load_dotenv

import test_data

load_dotenv("./.test.env")


@pytest.fixture
def mock_boto3_client():
    with patch("boto3.client") as mock_boto3:
        mock_timestream = MagicMock()
        mock_s3 = MagicMock()
        mock_boto3.side_effect = lambda service_name, *args, **kwargs: {
            "timestream-write": mock_timestream,
            "s3": mock_s3,
        }[service_name]
        yield mock_timestream, mock_s3


@pytest.fixture
def lambda_handler(mock_boto3_client):
    import main

    reload(main)
    return main.lambda_handler


@pytest.mark.parametrize("input_event", test_data.test_events_not_supported)
def test_empty_event_and_filtering(lambda_handler, mock_boto3_client, input_event):
    mock_timestream, mock_s3 = mock_boto3_client

    lambda_handler(input_event, None)

    assert not mock_timestream.write_records.called
    assert not mock_s3.write_records.called


@pytest.mark.parametrize(
    "input_event, expected_timestream_writes",
    test_data.test_events_with_timestream_calls,
)
def test_events(
    lambda_handler, mock_boto3_client, input_event, expected_timestream_writes
):
    mock_timestream, mock_s3 = mock_boto3_client

    lambda_handler(input_event, None)

    assert mock_timestream.write_records.call_args_list == expected_timestream_writes
    assert not mock_s3.write_records.called


@pytest.mark.parametrize(
    "input_event, expected_s3_puts",
    [(test_data.event_with_device_name, test_data.event_with_device_name_error_result)],
)
def test_error_handling(
    lambda_handler, mock_boto3_client, input_event, expected_s3_puts
):
    mock_timestream, mock_s3 = mock_boto3_client
    mock_timestream.exceptions.RejectedRecordsException = (
        test_data.MockRejectedRecordsException
    )
    mock_timestream.write_records.side_effect = test_data.MockRejectedRecordsException(
        test_data.rejected_records_response
    )

    with patch("uuid.uuid4", return_value="123-123"):
        lambda_handler(input_event, None)

    assert (
        mock_s3.put_object.call_args_list
        == test_data.event_with_device_name_error_result
    )
