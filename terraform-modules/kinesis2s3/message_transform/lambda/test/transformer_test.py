from dotenv import load_dotenv
import os

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
CASES_PATH_PREFIX = f"{TEST_ROOT}/cases"
load_dotenv(f"{TEST_ROOT}/.test.env")

import json
from unittest.mock import Mock, patch

import boto3
import pytest
from moto import mock_aws



@pytest.fixture
def import_message_transformer():
    from message_transformer import MessageTransformer

    return MessageTransformer


@pytest.fixture
def mock_clients():
    with mock_aws():
        boto3.setup_default_session(region_name="us-east-1")
        cloudwatch_mock = boto3.client("cloudwatch")
        with patch("main.cloudwatch", cloudwatch_mock):
            yield cloudwatch_mock



@pytest.fixture
def import_lambda_handler(mock_clients):
    from main import lambda_handler

    return lambda_handler


@pytest.mark.parametrize(
    "case_name", ["single_empty_value", "empty_in_array_of_good", "array_good"]
)
def test_messages_being_transformed_correctly(case_name, import_message_transformer):
    with open(f"{CASES_PATH_PREFIX}/input/{case_name}.json", "r") as f:
        input_data = json.loads(f.read().strip())

    with open(f"{CASES_PATH_PREFIX}/output/{case_name}.json", "r") as f:
        expected_output = json.loads(f.read().strip())

    transformer = import_message_transformer(Mock(), "plcf", "1")
    assert transformer.transform_record(input_data) == expected_output


@pytest.mark.parametrize(
    "case_name", ["multiple_records_factory_partition"]
)
def test_multiple_records_being_transformed_correctly(case_name, import_message_transformer):
    with open(f"{CASES_PATH_PREFIX}/input/{case_name}.json", "r") as f:
        input_data = json.loads(f.read().strip())

    with open(f"{CASES_PATH_PREFIX}/output/{case_name}.json", "r") as f:
        expected_output = json.loads(f.read().strip())

    transformer = import_message_transformer(Mock(), "plcf", "1")
    assert transformer.transform_encoded_records(input_data) == expected_output


@pytest.mark.parametrize(
    "case_name, topic_partitions, expected",
    [
        (
                "array_good_with_iottopic",
                "category,line",
                "array_good_extended_partitions",
        ),
        (
                "array_with_iottopic_overriding_default_partition",
                "category,line,year",
                "array_good_extended_partitions",
        ),
    ],
)
def test_messages_being_transformed_correctly_with_partitions_from_topic(
    case_name, topic_partitions, expected, import_message_transformer
):
    with open(f"{CASES_PATH_PREFIX}/input/{case_name}.json", "r") as f:
        input_data = json.loads(f.read().strip())

    with open(f"{CASES_PATH_PREFIX}/output/{expected}.json", "r") as f:
        expected_output = json.loads(f.read().strip())

    transformer = import_message_transformer(Mock(), "plcf", "1", topic_partitions)
    assert transformer.transform_record(input_data) == expected_output


@mock_aws
def test_whole_function(import_lambda_handler, mock_clients):
    with open(f"{CASES_PATH_PREFIX}/input/complete_mixed.json", "r") as f:
        event = json.loads(f.read().strip())

    with open(f"{CASES_PATH_PREFIX}/output/complete_mixed.json", "r") as f:
        expected_output = json.loads(f.read().strip())

    assert import_lambda_handler(event, None) == expected_output
