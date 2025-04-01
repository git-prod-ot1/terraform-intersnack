import dotenv

dotenv.load_dotenv(".env")

import pytest
import json
from io import StringIO
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from video_stream_data_archiver import video_stream_data_archiver
from video_stream_data_archiver.video_stream_data_archiver import (
    TimeRange,
    VideoStreamDataArchiver,
    TimeRangeDecoder,
    KinesisVideoEndpoints,
)

from datetime import timedelta
from datetime import datetime
from datetime import timezone

STREAM_NAME = "dev_mock_mockedfactory_test_stream_01"
STREAM = {
    "DeviceName": "MOCK",
    "StreamName": STREAM_NAME,
    "StreamARN": f"arn:aws:kinesisvideo:eu-central-1:000000000000:stream/{STREAM_NAME}/1703153271234",
    "MediaType": "video/h264",
    "KmsKeyId": "arn:aws:kms:eu-central-1:000000000000:alias/aws/kinesisvideo",
    "Version": "u0naWkMc2aHaJ5WQs8rN",
    "Status": "ACTIVE",
    "CreationTime": datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
    "DataRetentionInHours": 48,
}

STREAM_TO_FAIL_NAME="dev_mock_mockedfactory_test_stream_FAIL"

KVAM_LIST_FRAGMENTS_EMPTY = {
    "ResponseMetadata": {
        "RequestId": "21f3a2b5-93ea-4d74-be94-661246xv2420",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "Fragments": [],
}

KVAM_LIST_FRAGMENTS_SHORT_VIDEO_NO_TOKEN = {
    "ResponseMetadata": {
        "RequestId": "21f3a2b5-93ea-4d74-be94-661246xv2420",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "Fragments": [
        {
            "FragmentNumber": "start",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(2001, 1, 1, 12, tzinfo=timezone.utc),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 1000,
        },
        {
            "FragmentNumber": "consistent_fragment",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(
                2001, 1, 1, 12, 0, 1, 10000, tzinfo=timezone.utc
            ),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 1000,
        },
        {
            "FragmentNumber": "fragment_to_late",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(2001, 1, 1, 13, tzinfo=timezone.utc),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 1000,
        },
    ],
}

KVAM_LIST_FRAGMENTS_VIDEO_OF_0_LENGTH = {
    "ResponseMetadata": {
        "RequestId": "21f3a2b5-93ea-4d74-be94-661246xv2420",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "Fragments": [
        {
            "FragmentNumber": "start",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(2001, 1, 1, 12, tzinfo=timezone.utc),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 0,
        },
    ],
}

KVAM_LIST_FRAGMENTS_VIDEO_STARTING_BEFORE_LAST_TIMESTAMP = {
    "ResponseMetadata": {
        "RequestId": "21f3a2b5-93ea-4d74-be94-661246xv2420",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "Fragments": [
        {
            "FragmentNumber": "start",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(2001, 1, 1, 12, tzinfo=timezone.utc),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 300,
        },
    ],
}

KVAM_LIST_FRAGMENTS_WITH_TOKEN = {
    "ResponseMetadata": {
        "RequestId": "21f3a2b5-93ea-4d74-be94-661246xv2420",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "Fragments": [
        {
            "FragmentNumber": "fragment_with_token",
            "FragmentSizeInBytes": 123,
            "ProducerTimestamp": datetime(2001, 1, 1, 13, tzinfo=timezone.utc),
            "ServerTimestamp": None,
            "FragmentLengthInMilliseconds": 1000,
        }
    ],
    "NextToken": "nextTokenMock",
}

STREAM_LIST_ONE_ELEMENT = {"StreamInfoList": [STREAM]}
STREAM_LIST_EMPTY = {"StreamInfoList": []}
ENDPOINT_DATA = {
    "ResponseMetadata": {
        "RequestId": "c133e699-fabf-4947-8f64-287b35173143",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "DataEndpoint": "https://asdasdmock.com",
}

TEST_EVENT = {
    "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "account": "000000000000",
    "time": "2001-01-02 12:00:00.000Z",
    "region": "us-central-1",
    "resources": ["arn:aws:events:us-east-1:000000000000:rule/ExampleRule"],
    "detail": {},
}

TEST_EVENT_BEFORE_STEAM_CREATION_TIME = {
	"id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
	"detail-type": "Scheduled Event",
	"source": "aws.events",
	"account": "000000000000",
	"time": "2000-01-01 10:00:00.000Z",
	"region": "us-central-1",
	"resources": ["arn:aws:events:us-east-1:000000000000:rule/ExampleRule"],
	"detail": {},
}

@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_unit_get_all_video_fragments(boto3_mock):
    kvam_mock = mock_long_video__list_fragments_with_token(boto3_mock)
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()

    video_solution = VideoStreamDataArchiver(
        kc=Mock(), dynamodb=Mock(), s3=Mock(), kv=mock_active_stream(), sqs=Mock()
    )
    video_fragments = video_solution._VideoStreamDataArchiver__get_all_video_fragments(
        STREAM_NAME,
        TimeRange(
            start=datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
            end=datetime(2001, 1, 2, 12, tzinfo=timezone.utc),
        ),
        None
    )

    first_list_fragments_call_args = kvam_mock.method_calls[0][2]
    seconds_list_fragments_call_args = kvam_mock.method_calls[1][2]
    fragment_numbers = [f_number.get("FragmentNumber") for f_number in video_fragments]

    assert first_list_fragments_call_args.get("NextToken") is None
    assert seconds_list_fragments_call_args.get("NextToken") == "nextTokenMock"

    assert "start" in fragment_numbers
    assert "consistent_fragment" in fragment_numbers
    assert "fragment_to_late" in fragment_numbers
    assert "fragment_with_token" in fragment_numbers


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
@pytest.mark.parametrize(
    "last_processed_timestamp, video_lookup_from",
    [
        (
            datetime.timestamp(
                datetime(2001, 1, 2, 12, tzinfo=timezone.utc) - timedelta(days=3)
            ),
            datetime(2001, 1, 2, 12, tzinfo=timezone.utc) - timedelta(hours=48),
        ),
        (
            datetime.timestamp(
                datetime(2001, 1, 2, 12, tzinfo=timezone.utc) - timedelta(hours=2)
            ),
            datetime(2001, 1, 2, 12, tzinfo=timezone.utc) - timedelta(hours=2),
        ),
    ],
)
def test_awsmock_video_scann_time_range_dependent_on_last_processed_timestamp(
    boto3_mock,
    last_processed_timestamp,
    video_lookup_from,
):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_video(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        dynamodb=mock_video_last_processed_index(last_processed_timestamp),
        sqs=Mock(),
        kc=Mock(),
        kv=mock_active_stream(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    video_search_range = kvam_mock.list_fragments.call_args_list
    assert video_search_range[-1][1]["FragmentSelector"]["TimestampRange"] == {
        "StartTimestamp": video_lookup_from,
        "EndTimestamp": datetime(2001, 1, 2, 12, tzinfo=timezone.utc),
    }


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_video_scan_time_range_when_no_timestamp(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_no_video_fragments(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        kc=Mock(),
        dynamodb=mock_no_video_last_index(),
        s3=Mock(),
        kv=mock_active_stream(),
        sqs=Mock(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    fragments_search_args = kvam_mock.list_fragments.call_args_list
    assert fragments_search_args[-1][1]["FragmentSelector"]["TimestampRange"] == {
        "StartTimestamp": datetime(2001, 1, 2, 12, tzinfo=timezone.utc)
        - timedelta(hours=48),
        "EndTimestamp": datetime(2001, 1, 2, 12, tzinfo=timezone.utc),
    }


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_video_stream_created_after_start_of_process(boto3_mock):
    # Given
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_no_video_fragments(boto3_mock)

    video_solution = VideoStreamDataArchiver(
		dynamodb=mock_no_video_last_index(),
		sqs=Mock(),
		kc=Mock(),
		kv=mock_active_stream(),
	)

    # When
    video_solution.process_streams(TEST_EVENT_BEFORE_STEAM_CREATION_TIME, get_context_mock())

    # Then
    assert kvam_mock.list_fragments.call_count == 0


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_no_active_video(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_no_video_fragments(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        kc=Mock(),
        dynamodb=mock_no_video_last_index(),
        s3=Mock(),
        kv=mock_active_stream(),
        sqs=Mock(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    fragments_search_args = kvam_mock.list_fragments.call_args_list
    assert fragments_search_args[-1][1]["FragmentSelector"]["TimestampRange"] == {
        "StartTimestamp": datetime(2001, 1, 2, 12, tzinfo=timezone.utc)
        - timedelta(hours=48),
        "EndTimestamp": datetime(2001, 1, 2, 12, tzinfo=timezone.utc),
    }


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_no_active_stream(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_no_video_fragments(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        dynamodb=mock_video_last_processed_index(978340402.0),
        sqs=Mock(),
        kc=Mock(),
        kv=mock_no_active_streams(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    assert kvam_mock.list_fragments.call_count == 0


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_when_active_stream_get_all_fragments(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_video(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        dynamodb=mock_video_last_processed_index(978350400.0),
        sqs=Mock(),
        kc=Mock(),
        kv=mock_active_stream(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    get_all_fragments_args = kvam_mock.list_fragments.call_args_list[0][1]
    clip_selector = get_all_fragments_args["FragmentSelector"]
    assert (
        get_all_fragments_args["StreamName"] == "dev_mock_mockedfactory_test_stream_01"
    )
    assert clip_selector["FragmentSelectorType"] == "PRODUCER_TIMESTAMP"
    assert clip_selector["TimestampRange"]["StartTimestamp"] == datetime(
        2001, 1, 1, 12, 0, tzinfo=timezone.utc
    )
    assert clip_selector["TimestampRange"]["EndTimestamp"] == datetime(
        2001, 1, 2, 12, 0, tzinfo=timezone.utc
    )


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_clip_processing_request_in_sqs(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video(boto3_mock)
    sqs_mock = Mock()

    video_solution = VideoStreamDataArchiver(
        dynamodb=mock_video_last_processed_index(978350398.0),
        sqs=sqs_mock,
        kv=mock_active_stream(),
        kc=Mock(),
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    sqs_args = sqs_mock.send_message.call_args_list[0][1]
    queue_url = sqs_args["QueueUrl"]
    message_body = sqs_args["MessageBody"]
    assert (
        queue_url
        == "https://sqs.eu-central-1.amazonaws.com/093961187306/dev-plcf-videostreams"
    )
    assert (
        message_body
        == "{'PK': {'S': 'CLIP#dev_mock_mockedfactory_test_stream_01'}, 'SK': {'S': 'START#2001.01.01-12:00:00.000'}}"
    )


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_clip_current_process_timestamp_to_dynamodb(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video(boto3_mock)
    dynamodb_mock = mock_video_last_processed_index(978350400.0)

    video_solution = VideoStreamDataArchiver(
        dynamodb=dynamodb_mock, sqs=Mock(), kv=mock_active_stream(), kc=Mock()
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    db_args = dynamodb_mock.put_item.call_args_list[0][1]
    db_item_pk = db_args["Item"]["PK"]["S"]
    db_item_sk = db_args["Item"]["SK"]["S"]
    db_item_val = db_args["Item"]["current_timestamp"]["S"]
    assert db_item_pk == "FACTORY#mockedfactory"
    assert db_item_sk == "STREAM#dev_mock_mockedfactory_test_stream_01"
    assert (
        db_item_val
        == "{'stream_name': 'dev_mock_mockedfactory_test_stream_01', 'index': '978350402.01'}"
    )


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_clip_data_send_to_dynamodb(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video(boto3_mock)
    dynamodb_mock = mock_video_last_processed_index(978350400.0)

    video_solution = VideoStreamDataArchiver(
        dynamodb=dynamodb_mock, sqs=Mock(), kv=mock_active_stream(), kc=Mock()
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    db_args = dynamodb_mock.put_item.call_args_list[1][1]
    db_item_pk = db_args["Item"]["PK"]["S"]
    db_item_sk = db_args["Item"]["SK"]["S"]
    db_item_val = db_args["Item"]["clip_data"]["S"]
    clip_data = json.loads(db_item_val, cls=TimeRangeDecoder)
    assert db_item_pk == "CLIP#dev_mock_mockedfactory_test_stream_01"
    assert db_item_sk == "START#2001.01.01-12:00:00.000"
    assert clip_data.get("stream_name") == "dev_mock_mockedfactory_test_stream_01"
    assert clip_data.get("time_range") == TimeRange(
        start=datetime(2001, 1, 1, 12, 0, tzinfo=timezone.utc),
        end=datetime(2001, 1, 1, 12, 0, 2, 10000, tzinfo=timezone.utc),
    )
    assert clip_data.get("index_stream_name") == "dev_plcf_testmock_video_index_process"


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_drop_zero_length_clips(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video_of_zero_length(boto3_mock)
    dynamodb_mock = mock_video_last_processed_index(978350400.0)
    sqs_mock = Mock()

    video_solution = VideoStreamDataArchiver(
        dynamodb=dynamodb_mock, sqs=sqs_mock, kv=mock_active_stream(), kc=Mock()
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    # assert dynamodb_mock.put_item.call_count == 1  # move last processed time index
    assert sqs_mock.send_message.call_count == 0


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_drop_clip_before_end_timestamp(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video_before_last_timestamp(boto3_mock)
    dynamodb_mock = mock_video_last_processed_index(978350700.0)

    video_solution = VideoStreamDataArchiver(
        dynamodb=dynamodb_mock, sqs=Mock(), kv=mock_active_stream(), kc=Mock()
    )
    video_solution.process_streams(TEST_EVENT, get_context_mock())

    assert dynamodb_mock.put_item.call_count == 0

@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_unit_fetch_streams_list(boto3_mock):
    stream_name_with_matching_prefix = __create_mock_stream_definition("MCKEB4C1B1C01_apan_02_1_test")
    stream_name_with_unmatching_prefix = __create_mock_stream_definition("ABCEB4C1B1C01_apan_02_1_test")
    video_solution = VideoStreamDataArchiver(
		kc=Mock(),
		dynamodb=Mock(),
		s3=Mock(),
		kv=mock_active_streams([STREAM, stream_name_with_matching_prefix, stream_name_with_unmatching_prefix]),
		sqs=Mock()
	)
    streams_list = video_solution._VideoStreamDataArchiver__fetch_streams_list()
    assert len(streams_list) is 2
    assert STREAM in streams_list
    assert stream_name_with_matching_prefix in streams_list

@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
@patch("video_stream_data_archiver.video_stream_data_archiver.kinesis_video_endpoints_cache")
def test_process_streams_with_resource_not_found_exception(boto3_mock, mock_kv_endpoints_cache):
    # Given
    kv_mock=mock_with_failed_streams()
    kvam_mock = mock_video(boto3_mock)
    mock_video_endpoints_cache(mock_kv_endpoints_cache, kvam_mock)

    video_stream_data_archiver.kinesis_video_endpoints_cache = mock_kv_endpoints_cache
    video_solution = VideoStreamDataArchiver(
        dynamodb=mock_video_last_processed_index(978350400.0),
        sqs=Mock(),
        kc=Mock(),
        kv=kv_mock,
    )

    # When
    video_solution.process_streams(TEST_EVENT, get_context_mock_for_2_streams())

    # Then
    get_all_fragments_args = kvam_mock.list_fragments.call_args_list[0][1]
    clip_selector = get_all_fragments_args["FragmentSelector"]
    assert (
            get_all_fragments_args["StreamName"] == "dev_mock_mockedfactory_test_stream_01"
    )
    assert clip_selector["FragmentSelectorType"] == "PRODUCER_TIMESTAMP"
    assert clip_selector["TimestampRange"]["StartTimestamp"] == datetime(
        2001, 1, 1, 12, 0, tzinfo=timezone.utc
    )
    assert clip_selector["TimestampRange"]["EndTimestamp"] == datetime(
        2001, 1, 2, 12, 0, tzinfo=timezone.utc
    )

def test_awsmock_no_time_left():
    kv_mock = mock_active_stream()
    mock_video()

    video_solution = VideoStreamDataArchiver(
        kv=kv_mock, kc=Mock(), sqs=Mock(), dynamodb=mock_video_last_processed_index(123)
    )
    video_solution.process_streams(TEST_EVENT, context_mock_1ms_left())

    assert len(kv_mock.list_streams.mock_calls) is 1
    assert len(kv_mock.list_fragments.mock_calls) is 0


def mock_video(boto3_mock=Mock()):
    kvam_mock = Mock()
    kvam_mock.list_fragments.side_effect = [
        KVAM_LIST_FRAGMENTS_SHORT_VIDEO_NO_TOKEN,
    ]
    kvam_mock.get_clip.return_value = {"Payload": StringIO("clipmock")}
    boto3_mock.client.return_value = kvam_mock
    return kvam_mock


def mock_video_of_zero_length(boto3_mock=Mock()):
    kvam_mock = Mock()
    kvam_mock.list_fragments.side_effect = [
        KVAM_LIST_FRAGMENTS_VIDEO_OF_0_LENGTH,
    ]
    kvam_mock.get_clip.return_value = {"Payload": StringIO("clipmock")}
    boto3_mock.client.return_value = kvam_mock
    return kvam_mock


def mock_video_before_last_timestamp(boto3_mock=Mock()):
    kvam_mock = Mock()
    kvam_mock.list_fragments.side_effect = [
        KVAM_LIST_FRAGMENTS_VIDEO_STARTING_BEFORE_LAST_TIMESTAMP,
    ]
    kvam_mock.get_clip.return_value = {"Payload": StringIO("clipmock")}
    boto3_mock.client.return_value = kvam_mock
    return kvam_mock


def get_context_mock():
    context_mock = Mock()
    context_mock.get_remaining_time_in_millis.side_effect = [3 * 60 * 1000, 2000]
    return context_mock


def get_context_mock_for_2_streams():
    context_mock = Mock()
    context_mock.get_remaining_time_in_millis.side_effect = [3 * 60 * 1000, 3 * 60 * 1000 - 1, 2000]
    return context_mock

def context_mock_1ms_left():
    context_mock = Mock()
    context_mock.get_remaining_time_in_millis.return_value = 1
    return context_mock


def mock_active_stream():
    kv_mock = Mock()
    kv_mock.list_streams.return_value = STREAM_LIST_ONE_ELEMENT
    kv_mock.get_data_endpoint.return_value = ENDPOINT_DATA
    return kv_mock

def mock_no_video_fragments(boto3_mock):
    kvam_mock = Mock()
    kvam_mock.list_fragments.return_value = KVAM_LIST_FRAGMENTS_EMPTY
    boto3_mock.client.return_value = kvam_mock
    return kvam_mock


def mock_no_active_streams():
    kv_mock = Mock()
    kv_mock.list_streams.return_value = STREAM_LIST_EMPTY
    kv_mock.get_data_endpoint.return_value = ENDPOINT_DATA
    return kv_mock

def mock_active_streams(streams):
    kv_mock = Mock()
    kv_mock.list_streams.return_value = {"StreamInfoList": streams}
    return kv_mock

def mock_with_failed_streams():
    kv_mock = Mock()
    kv_mock.list_streams.return_value = {"StreamInfoList": [__create_mock_stream_definition(STREAM_TO_FAIL_NAME), STREAM]}
    kv_mock.get_data_endpoint.return_value = ENDPOINT_DATA
    return kv_mock


def mock_video_last_processed_index(last_processed_index):
    dynamodb_mock = Mock()
    dynamodb_mock.batch_get_item.return_value = {
        "Responses": {
            "dev_plcf_videostreams": [
                {
                    "current_timestamp": {
                        "S": f"{{'stream_name': 'dev_mock_mockedfactory_test_stream_01', 'index': '{last_processed_index}'}}"
                    }
                }
            ]
        }
    }
    return dynamodb_mock


def mock_long_video__list_fragments_with_token(boto3_mock):
    kvam_mock = Mock()
    kvam_mock.list_fragments.side_effect = [
        KVAM_LIST_FRAGMENTS_WITH_TOKEN,
        KVAM_LIST_FRAGMENTS_SHORT_VIDEO_NO_TOKEN,
    ]
    kvam_mock.get_clip.return_value = {"Payload": StringIO("clipmock")}
    boto3_mock.client.return_value = kvam_mock
    return kvam_mock


def mock_no_video_last_index():
    dynamodb_mock = Mock()
    dynamodb_mock.batch_get_item.return_value = {
        "Responses": {"dev_plcf_videostreams": []}
    }
    return dynamodb_mock

def __prepare_streams_by_stream_names(stream_names):
    stream_info_list=[]
    for name in stream_names:
        stream_info_list.append(__create_mock_stream_definition(name))
    return stream_info_list

def __create_mock_stream_definition(stream_name: str):
    return {
		"DeviceName": "MOCK",
		"StreamName": stream_name,
		"StreamARN": f"arn:aws:kinesisvideo:eu-central-1:000000000000:stream/{stream_name}/1703153271234",
		"MediaType": "video/h264",
		"KmsKeyId": "arn:aws:kms:eu-central-1:000000000000:alias/aws/kinesisvideo",
		"Version": "u0naWkMc2aHaJ5WQs8rN",
		"Status": "ACTIVE",
		"CreationTime": datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
		"DataRetentionInHours": 48,
	}

def mock_video_endpoints_cache(mock_kv_endpoints_cache, kvam_mock):
    def side_effect(stream_name, kv):
        if stream_name == STREAM_NAME:
            return kvam_mock
        else:
            raise define_resource_not_found_exception()
    mock_kv_endpoints_cache.endpoint.side_effect = side_effect

def define_resource_not_found_exception():
    error_response = {
        'Error': {
            'Code': 'ResourceNotFoundExceptions',
            'Message': 'The requested resource was not found'
        }
    }
    return ClientError(error_response, 'DescribeResource')
