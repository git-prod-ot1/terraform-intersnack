import dotenv

dotenv.load_dotenv(".env")

import datetime
import json

from botocore.exceptions import ClientError
from datetime import datetime
from datetime import timezone

from io import StringIO
from unittest.mock import Mock, patch

from video_stream_data_archiver import video_stream_data_archiver
from video_stream_data_archiver.video_stream_data_archiver import (
    VideoStreamDataArchiver,
    KinesisVideoEndpoints,
)

SQS_MESSAGE = (
    "{'PK': {'S': 'CLIP#dev_mock_mockedfactory_test_stream_01'}, 'SK': {'S': "
    "'START#2001.01.01-12:00:00.000'}}"
)
SQS_EVENT = {
    "Records": [
        {
            "messageId": "message-1",
            "receiptHandle": "handle-1",
            "body": "{'PK': {'S': 'CLIP#ok'}, 'SK': {'S': 'START#2001.01.01-12:00:00.000'}}",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1523232000000",
                "SenderId": "123456789012",
                "ApproximateFirstReceiveTimestamp": "1523232000001",
            },
            "messageAttributes": {},
            "md5OfBody": "{{{md5_of_body}}}",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
            "awsRegion": "us-east-1",
        },
    ]
}
ENDPOINT_DATA = {
    "ResponseMetadata": {
        "RequestId": "c133e699-fabf-4947-8f64-287b35173143",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
    },
    "DataEndpoint": "https://asdasdmock.com",
}
MOCKED_DYNAMODB_RECORD = (
    "{'stream_name': 'dev_mock_mockedfactory_test_stream_01', 'time_range': {'__time_range__': "
    "true,"
    "'start': '2024-01-31T14:10:16.826000+00:00', 'end': '2024-01-31T14:11:43.778000+00:00'}, "
    "'video_bucket_name': 'dev-plcf-video-feed', 'index_stream_name': 'dev_plcf_testtsarray_video_index_process'}"
)
MOCKED_ZERO_LEGTH_CLIP_RECORD = (
    "{'stream_name': 'dev_mock_mockedfactory_test_stream_01', 'time_range': {'__time_range__': "
    "true,"
    "'start': '2024-01-31T14:11:16.826000+00:00', 'end': '2024-01-31T14:11:16.826000+00:00'}, "
    "'video_bucket_name': 'dev-plcf-video-feed', 'index_stream_name': "
    "'dev_plcf_testtsarray_video_index_process'}"
)


#  todo: test dropping 0 length video?
#  todo: test VideoToShort exception?


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_save_video_to_s3(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video_clip(boto3_mock)
    s3_mock = mock_s3()

    video_solution = VideoStreamDataArchiver(
        s3=s3_mock,
        dynamodb=mock_dynamodb_clip_data(),
        kv=mock_video_endpoint(),
        kc=mock_kinesis(),
        sqs=Mock(),
    )
    video_solution._VideoStreamDataArchiver__process_record(SQS_MESSAGE)

    video_upload_args = s3_mock.put_object.call_args_list[0][1]
    assert video_upload_args["Body"] == "clipmock"
    assert video_upload_args["ContentType"] == "media/mp4"
    assert (
        video_upload_args["Key"]
        == "stream=dev_mock_mockedfactory_test_stream_01/year=2024/month=1/day=31/hour=14/video-14:10:16.826.mp4"
    )


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_send_datapoint(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    mock_video_clip(boto3_mock)
    kc_mock = mock_kinesis()

    video_solution = VideoStreamDataArchiver(
        s3=mock_s3(),
        dynamodb=mock_dynamodb_clip_data(),
        kv=mock_video_endpoint(),
        kc=kc_mock,
        sqs=Mock(),
    )
    video_solution._VideoStreamDataArchiver__process_record(SQS_MESSAGE)

    kinesis_put_record_args = kc_mock.put_record.call_args_list[0][1]
    kinesis_record = json.loads(kinesis_put_record_args["Data"])
    assert kinesis_record["dataPointId"] == "dev_mock_mockedfactory_test_stream_01"
    assert kinesis_record["takenAt"] == "2024-01-31 14:10:16.826"
    assert kinesis_record["takenAtEnd"] == "2024-01-31 14:11:43.778"
    assert (
        kinesis_record["value"]
        == "stream=dev_mock_mockedfactory_test_stream_01/year=2024/month=1/day=31/hour=14/video-14:10:16.826.mp4"
    )
    assert (
        kinesis_put_record_args["StreamName"]
        == "dev_plcf_testtsarray_video_index_process"
    )
    assert kinesis_record["month"] == "01"
    assert kinesis_record["day"] == "31"
    assert kinesis_record["year"] == "2024"


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_drop_clip_to_short(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_get_clip_to_short_video_exception(boto3_mock)
    kc_mock = mock_kinesis()
    s3_mock = mock_s3()

    video_solution = VideoStreamDataArchiver(
        s3=s3_mock,
        dynamodb=mock_dynamodb_clip_data(),
        kv=mock_video_endpoint(),
        kc=kc_mock,
        sqs=Mock(),
    )
    video_solution._VideoStreamDataArchiver__process_record(SQS_MESSAGE)

    assert kvam_mock.get_clip.call_count == 1
    assert kc_mock.put_record.call_count == 0
    assert s3_mock.put_object.call_count == 0


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_drop_0_length_clip(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_video_clip(boto3_mock)
    kc_mock = mock_kinesis()

    video_solution = VideoStreamDataArchiver(
        s3=mock_s3(),
        dynamodb=mock_dynamodb_zero_length_clip_data(),
        kv=mock_video_endpoint(),
        kc=kc_mock,
        sqs=Mock(),
    )
    video_solution._VideoStreamDataArchiver__process_record(SQS_MESSAGE)

    assert kvam_mock.get_clip.call_count == 0


@patch("video_stream_data_archiver.video_stream_data_archiver.boto3")
def test_awsmock_get_video_clip(boto3_mock):
    video_stream_data_archiver.kinesis_video_endpoints_cache = KinesisVideoEndpoints()
    kvam_mock = mock_video_clip(boto3_mock)

    video_solution = VideoStreamDataArchiver(
        s3=mock_s3(),
        dynamodb=mock_dynamodb_clip_data(),
        kv=mock_video_endpoint(),
        kc=mock_kinesis(),
        sqs=Mock(),
    )
    video_solution._VideoStreamDataArchiver__process_record(SQS_MESSAGE)

    get_clip_args = kvam_mock.get_clip.call_args_list[0][1]
    clip_selector = get_clip_args["ClipFragmentSelector"]
    assert get_clip_args["StreamName"] == "dev_mock_mockedfactory_test_stream_01"
    assert clip_selector["FragmentSelectorType"] == "PRODUCER_TIMESTAMP"
    assert (
        clip_selector["TimestampRange"]["StartTimestamp"]
        == f"{datetime(2024, 1, 31, 14, 10, 16, 826000, tzinfo=timezone.utc)}"
    )
    assert (
        clip_selector["TimestampRange"]["EndTimestamp"]
        == f"{datetime(2024, 1, 31, 14, 11, 43, 778000, tzinfo=timezone.utc)}"
    )


def mock_video_clip(boto3_mock):
    kvam_mock = Mock()
    boto3_mock.client.return_value = kvam_mock
    kvam_mock.get_clip.return_value = {"Payload": StringIO("clipmock")}
    return kvam_mock


def mock_get_clip_to_short_video_exception(boto3_mock):
    kvam_mock = Mock()
    boto3_mock.client.return_value = kvam_mock
    kvam_mock.get_clip.side_effect = ClientError(
        {
            "Error": {
                "Code": "InvalidArgumentException",
                "Message": "StartTimestamp must be before EndTimestamp",
            }
        },
        "operation_name",
    )
    return kvam_mock


def mock_video_endpoint():
    kv_mock = Mock()
    kv_mock.get_data_endpoint.return_value = ENDPOINT_DATA
    return kv_mock


def mock_s3():
    s3_mock = Mock()
    s3_mock.put_object.return_value = "ok"
    return s3_mock


def mock_kinesis():
    kc_mock = Mock()
    kc_mock.put_record.return_value = "ok"
    return kc_mock


def mock_dynamodb_clip_data():
    dynamodb_mock = Mock()
    dynamodb_mock.get_item.return_value = {
        "Item": {"clip_data": {"S": MOCKED_DYNAMODB_RECORD}}
    }
    return dynamodb_mock


def mock_dynamodb_zero_length_clip_data():
    dynamodb_mock = Mock()
    dynamodb_mock.get_item.return_value = {
        "Item": {"clip_data": {"S": MOCKED_ZERO_LEGTH_CLIP_RECORD}}
    }
    return dynamodb_mock
