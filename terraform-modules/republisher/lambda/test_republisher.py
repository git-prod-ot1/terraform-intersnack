import json

from dotenv import load_dotenv

load_dotenv("./.test.env")
import boto3

# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE

import pytest
from unittest.mock import MagicMock

import main


DATAPOINT_AA = {
    "dataPointId": "aa",
    "deviceName": "test",
    "value": 1,
    "takenAt": "2024-09-03T08:45:25.880Z",
    "postedAt": "2024-09-03T08:45:25.929Z",
    "modelVersion": "0.1.0",
    "configurationModelVersion": "0.1.0",
}
DATAPOINT_BB = {
    "dataPointId": "bb",
    "deviceName": "test",
    "value": 14.405553804881555,
    "takenAt": "2024-09-03T08:45:25.918Z",
    "postedAt": "2024-09-03T08:45:25.928Z",
    "modelVersion": "0.1.0",
    "configurationModelVersion": "0.1.0",
}
DATAPOINT_CC = {
    "dataPointId": "cc",
    "deviceName": "test",
    "value": 88,
    "takenAt": "2024-09-03T08:45:25.928Z",
    "postedAt": "2024-09-03T08:45:25.948Z",
    "modelVersion": "0.1.0",
    "configurationModelVersion": "0.1.0",
}
TEST_CONFIG = {
    "defaultTopic": "dev_plcf_testtsarray_data/republished/${datapointid}",
    "republish_all": False,
    "aa": {
        "republish": True,
        "topic": "dev_plcf_testtsarray_data/republished/${devicename}/${datapointid}",
    },
    "bb": {
        "republish": True,
        "topic": "dev_plcf_testtsarray_data/republished/${deviceName}/${dataPointId}",
        "transformation": {
            "cloudAdd": "lower: ${datapointid}, camel: ${datapointid}, upper: ${DATAPOINTID}"
        },
    },
    "cc": {
        "republish": True,
        "topic": "dev_plcf_testtsarray_data/republished/${asdasd}/${datapointid}",
        "transformation": {
            "cloudAdd": "lower: ${datapointid}, camel: ${datapointid}, upper: ${DATAPOINTID}"
        },
    },
}
TRANSFORMED_DATAPOINT_BB = {
    "dataPointId": "bb",
    "deviceName": "test",
    "value": 14.405553804881555,
    "takenAt": "2024-09-03T08:45:25.918Z",
    "postedAt": "2024-09-03T08:45:25.928Z",
    "modelVersion": "0.1.0",
    "configurationModelVersion": "0.1.0",
    "cloudAdd": "lower: bb, camel: bb, upper: bb",
}
TRANSFORMED_DATAPOINT_CC = {
    "dataPointId": "cc",
    "deviceName": "test",
    "value": 88,
    "takenAt": "2024-09-03T08:45:25.928Z",
    "postedAt": "2024-09-03T08:45:25.948Z",
    "modelVersion": "0.1.0",
    "configurationModelVersion": "0.1.0",
    "cloudAdd": "lower: cc, camel: cc, upper: cc",
}


@pytest.mark.parametrize(
    "measurement, expected_transformation, expected_topic",
    [
        (DATAPOINT_AA, DATAPOINT_AA, "dev_plcf_testtsarray_data/republished/test/aa"),
        (
          DATAPOINT_BB,
          TRANSFORMED_DATAPOINT_BB,
          "dev_plcf_testtsarray_data/republished/test/bb",
        ),
        (
          DATAPOINT_CC,
          TRANSFORMED_DATAPOINT_CC,
          "dev_plcf_testtsarray_data/republished/${asdasd}/cc",
        ),
    ],
)
def test_process_measurements(measurement, expected_transformation, expected_topic):
    main.reference_table["content"] = TEST_CONFIG
    mqqt_mock = MagicMock()

    main.republish(mqqt_mock, [measurement])

    mqqt_mock.publish.assert_called_with(
        expected_topic, json.dumps(expected_transformation), QoS=0
    )
