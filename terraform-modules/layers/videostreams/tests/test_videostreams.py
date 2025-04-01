import datetime
from unittest.mock import Mock, patch

import dotenv
import pytest

dotenv.load_dotenv(".test.env")
from videostreams import videostreams

STREAM = {
    "StreamName": "some_stream_name",
    "DataRetentionInHours": 48
}


def mock_all_data_available(kvm, stream, time_range):
    return {"min": time_range[0], "max": time_range[1]}


def mock_all_data_but_newest_available(kvm, stream, time_range):
    if time_range[1] == 1695417660:
        return None
    return mock_all_data_available(kvm, stream, time_range)


@patch("videostreams.videostreams.get_min_and_max_timestamps")
@pytest.mark.parametrize('now_timestamp, last_timestamp, validate_function_mock, expected', [
    (1695417584, 1695417164, mock_all_data_available,
     [(1695417164, 1695417210),
      (1695417210, 1695417300),
      (1695417300, 1695417390),
      (1695417390, 1695417480),
      (1695417480, 1695417570)],
     ),
    (1695417584, 1695417164, mock_all_data_but_newest_available,
     [(1695417164, 1695417210),
      (1695417210, 1695417300),
      (1695417300, 1695417390),
      (1695417390, 1695417480)
      ],
     )
])
def test_determine_time_ranges_to_process(min_max_mock, now_timestamp, last_timestamp, validate_function_mock,
                                          expected):
    videostreams.initialize_clients()
    kvam = Mock()
    kvam.list_fragments.return_value = "Some fragments available"
    min_max_mock.side_effect = validate_function_mock

    actual = videostreams.determine_time_ranges_to_process(STREAM, kvam, now_timestamp, last_timestamp)
    assert actual == expected


def test_finding_min_max():
    # given
    kvam = Mock()
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    fragment_length = 1234
    kvam.list_fragments.return_value = {
        "Fragments": [{
            "ProducerTimestamp": now,
            "FragmentLengthInMilliseconds": fragment_length
        }]
    }
    range_mock = (1695417164, 1695417210)  # just whatever

    # when
    min_max = videostreams.get_min_and_max_timestamps(kvam, "stream_name", range_mock)
    now_timestamp = int(now.timestamp())
    fragment_end = now + datetime.timedelta(milliseconds=fragment_length)
    fragment_end_timestamp = int(fragment_end.timestamp())

    # then
    assert min_max == {"min": now_timestamp, "max": fragment_end_timestamp}


def test_real():
    videostreams.initialize_clients()
    videostreams.process_stream({
        "StreamName": "dev_plcf_kj_stream_debug_01",
        "DataRetentionInHours": 48
    }, int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()))
