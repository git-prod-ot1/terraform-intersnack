import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

BUCKET_NAME = "test-namespace-edgemonitoring-measurement-samples"

EVENT_WITH_TIME = {
    "glue_database": "test_namespace_measurement_samples_database",
    "glue_table": "samplesdata",
    "s3_location": f"s3://{BUCKET_NAME}/data/",
    "time": {"start": f"2024-12-24", "end": f"2025-01-02"},
}
EVENT_WITHOUT_TIME = {
    "glue_database": "test_namespace_measurement_samples_database",
    "glue_table": "samplesdata",
    "s3_location": f"s3://{BUCKET_NAME}/data/",
}
EVENT_WITH_FACTORY_IN_S3_LOCATION = {
    "glue_database": "test_namespace_measurement_samples_database",
    "glue_table": "samplesdata",
    "s3_location": f"s3://{BUCKET_NAME}/data/factory=factoryIn/",
    "time": {"start": f"2024-12-24", "end": f"2025-01-02"},
}


@pytest.fixture
def set_environment_vars():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["COMPANY_NAMESPACE"] = "namespace"
    os.environ["STAGE"] = "stage"
    os.environ["UNIT_NAME"] = "mock"


@pytest.fixture
def mock_clients(set_environment_vars):
    with mock_aws():
        boto3.setup_default_session(region_name="us-east-1")
        glue = MagicMock()
        s3 = boto3.client("s3", region_name="us-east-1")
        with patch("main.glue", glue):
            with patch("main.s3", boto3.resource("s3")):
                with patch("main.current_datetime", mock_current_datetime):
                    yield glue, s3


@pytest.fixture
def import_main(set_environment_vars, mock_clients):
    import main

    return main.handle_event


@mock_aws
def test_glue_partitioner_with_time(import_main, mock_clients):
    glue_mock, s3_client = mock_clients
    setup_default_s3_files_and_no_glue_partitions(glue_mock, s3_client)

    handle_event = import_main

    handle_event(EVENT_WITH_TIME)

    partition_input_values = get_partitions_created_call_arg_list(glue_mock)

    assert len(partition_input_values) == 6
    assert ["factoryBefore", "aaa", "2024", "12", "24"] in partition_input_values
    assert ["factoryIn", "bbb", "2024", "12", "25"] in partition_input_values
    assert ["factoryIn", "ccc", "2024", "12", "30"] in partition_input_values
    assert ["factoryIn", "ddd", "2024", "12", "31"] in partition_input_values
    assert ["factoryIn", "eee", "2025", "1", "1"] in partition_input_values
    assert ["factoryAfter", "b1", "2025", "1", "2"] in partition_input_values


@mock_aws
def test_glue_partitioner_with_factory_in_location(import_main, mock_clients):
    glue_mock, s3_client = mock_clients
    setup_default_s3_files_and_no_glue_partitions(glue_mock, s3_client)

    handle_event = import_main

    handle_event(EVENT_WITH_FACTORY_IN_S3_LOCATION)

    partition_input_values = get_partitions_created_call_arg_list(glue_mock)

    assert len(partition_input_values) == 4
    assert ["bbb", "2024", "12", "25"] in partition_input_values
    assert ["ccc", "2024", "12", "30"] in partition_input_values
    assert ["ddd", "2024", "12", "31"] in partition_input_values
    assert ["eee", "2025", "1", "1"] in partition_input_values


@mock_aws
def test_glue_partitioner_without_time(import_main, mock_clients):
    glue_mock, s3_client = mock_clients
    setup_default_s3_files_and_no_glue_partitions(glue_mock, s3_client)

    handle_event = import_main

    handle_event(EVENT_WITHOUT_TIME)

    partition_input_values = get_partitions_created_call_arg_list(glue_mock)

    assert len(partition_input_values) == 4
    assert ["factoryIn", "bbb", "2024", "12", "25"] in partition_input_values
    assert ["factoryIn", "ccc", "2024", "12", "30"] in partition_input_values
    assert ["factoryIn", "ddd", "2024", "12", "31"] in partition_input_values
    assert ["factoryIn", "eee", "2025", "1", "1"] in partition_input_values


@mock_aws
def test_glue_partitioner_critical_depth(import_main, mock_clients):
    glue_mock, s3_client = mock_clients
    setup_too_deep_nested_files_and_no_glue_partitions(glue_mock, s3_client)

    handle_event = import_main

    handle_event(EVENT_WITHOUT_TIME)

    partition_input_values = get_partitions_created_call_arg_list(glue_mock)

    assert len(partition_input_values) == 3
    assert ["f1", "a1", "s3", "s4", "s5", "2024", "12", "31"] in partition_input_values
    assert ["f2", "a2", "2024", "12", "31"] in partition_input_values
    assert ["f6", "2024", "12", "31"] in partition_input_values


def get_partitions_created_call_arg_list(glue_mock):
    partitions_created_call_arg_list = glue_mock.create_partition.call_args_list
    partition_input_values = [
        call_arg[1]["PartitionInput"]["Values"]
        for call_arg in partitions_created_call_arg_list
    ]
    return partition_input_values


def setup_too_deep_nested_files_and_no_glue_partitions(glue_mock, s3_client):
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f1/sub2=a1/sub3=s3/sub4=s4/sub5=s5/year=2024/month=12/day=31/file.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f2/sub2=a2/year=2024/month=12/day=31/file.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f3/sub2=a1/sub3=s3/sub4=s4/sub5=s5/sub6=s6/year=2024/month=12/day=31/file.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f4/sub2=a1/sub3=s3/sub4=s4/sub5=s5/sub6=s6/sub7=s7/sub8=s8/year=2024/month=12/file.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f5/year=2024/month=12/file.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=f6/year=2024/month=12/day=31/file.txt",
        Body=b"",
    )
    glue_mock.get_partition.side_effect = ClientError(
        {
            "Error": {
                "Code": "EntityNotFoundException",
                "Message": "Mock",
            }
        },
        "mock",
    )


def setup_default_s3_files_and_no_glue_partitions(glue_mock, s3_client):
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryBefore/subtopic2=a1/year=2024/month=1/day=31/file1.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryBefore/subtopic2=a2/year=2024/month=11/day=30/file2.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryBefore/subtopic2=a3/year=2024/month=12/day=01/file3.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryBefore/subtopic2=a4/year=2024/month=12/day=23/file4.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryBefore/subtopic2=aaa/year=2024/month=12/day=24/file5.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryIn/subtopic=bbb/year=2024/month=12/day=25/file6.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryIn/subtopic=ccc/year=2024/month=12/day=30/file7.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryIn/subtopic=ddd/year=2024/month=12/day=31/file8.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryIn/subtopic=eee/year=2025/month=1/day=1/file9.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryAfter/subtopic=b1/year=2025/month=1/day=2/file10.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryAfter/subtopic=b2/year=2025/month=1/day=3/file11.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryAfter/subtopic=b3/year=2025/month=1/day=8/file12.txt",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"data/factory=factoryAfter/subtopic=b4/year=2025/month=2/day=8/file13.txt",
        Body=b"",
    )
    glue_mock.get_partition.side_effect = ClientError(
        {
            "Error": {
                "Code": "EntityNotFoundException",
                "Message": "Mock",
            }
        },
        "mock",
    )


def mock_current_datetime():
    return datetime(2025, 1, 1, 0, 0, 0)
