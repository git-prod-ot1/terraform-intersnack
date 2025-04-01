import datetime
import itertools
import json
import logging
import os
import time
import traceback

import boto3

kv = None
kc = None
s3 = None

VIDEO_LENGTH_IN_SECONDS = None
MAX_COPY_ATTEMPTS = None
BUCKET_NAME = None
INDEX_STREAM_NAME = None
LAST_PROCESSING_TIMESTAMPS_PREFIX = None
VIDEO_INDEX_PREFIX = None
PROCESSING_ERRORS_PREFIX = None
STAGE = None
DRY_RUN = None
logger = logging.getLogger("videostreams")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def process_streams(event):
    streams = fetch_streams_list()
    process_start = datetime.datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
    logger.info(f"Using time {process_start} as process start")

    for stream in streams:
        try:
            logger.info(f"Processing stream '{stream}'")
            process_stream(stream, int(process_start.timestamp()))
        except Exception as e:
            logger.info(f"Could not process stream '{stream['StreamName']}', {str(e)}")
            traceback.print_exc()


def initialize_clients():
    logger.info('Initializing clients!')
    global s3, kv, kc, VIDEO_LENGTH_IN_SECONDS, MAX_COPY_ATTEMPTS, BUCKET_NAME, \
        LAST_PROCESSING_TIMESTAMPS_PREFIX, PROCESSING_ERRORS_PREFIX, \
        VIDEO_INDEX_PREFIX, INDEX_BUCKET_NAME, INDEX_STREAM_NAME, FACTORY, STAGE, COMPANY_NAMESPACE, DRY_RUN
    VIDEO_LENGTH_IN_SECONDS = int(os.environ.get('VIDEO_LENGTH_IN_SECONDS') or 90)
    MAX_COPY_ATTEMPTS = int(os.environ.get('MAX_COPY_ATTEMPTS') or 5)
    BUCKET_NAME = os.environ['BUCKET_NAME']
    LAST_PROCESSING_TIMESTAMPS_PREFIX = os.environ['LAST_PROCESSING_TIMESTAMPS_PREFIX']
    PROCESSING_ERRORS_PREFIX = os.environ['PROCESSING_ERRORS_PREFIX']
    INDEX_STREAM_NAME = os.environ['INDEX_STREAM_NAME']
    COMPANY_NAMESPACE = os.environ['COMPANY_NAMESPACE']
    FACTORY = os.environ['FACTORY']
    STAGE = os.environ['STAGE']
    DRY_RUN = os.environ.get("DRY_RUN") == "1" or False
    s3 = boto3.client('s3')
    kv = boto3.client("kinesisvideo")
    kc = boto3.client("kinesis")


def fetch_streams_list():
    streams_info = kv.list_streams(
        MaxResults=1000
    )["StreamInfoList"]
    # todo: fix with proper condition
    streams = [stream for stream in streams_info if
               stream["StreamName"].startswith(f"{STAGE}_{COMPANY_NAMESPACE}_{FACTORY}")]

    return streams


def process_stream(stream, process_start):
    stream_name = stream['StreamName']
    kvam = build_kinesis_client(stream_name)
    last_timestamp = get_stream_last_processing_time(stream_name)
    time_ranges = determine_time_ranges_to_process(stream, kvam, process_start, last_timestamp)
    logger.info(f"time ranges = {time_ranges}")

    for clip_start_time, clip_end_time in time_ranges:
        try:
            fetch_and_save_clip(stream_name, kvam, clip_start_time, clip_end_time)
        except Exception as e:
            logger.error(f"Could not process stream range, stream = {stream_name}, "
                         f"clip_start_time = {__format_timestamp(clip_start_time)}"
                         f"clip_end_time = {__format_timestamp(clip_end_time)}"
                         f": {str(e)}")
            key = generate_s3_error_key(stream_name, clip_start_time)
            put_stream_processing_error(key, str(e))
            put_stream_last_processing_time(stream_name, str(clip_end_time))


def build_kinesis_client(stream_name):
    endpoint = kv.get_data_endpoint(
        StreamName=stream_name,
        APIName="GET_CLIP"
    )

    return boto3.client("kinesis-video-archived-media", endpoint_url=endpoint["DataEndpoint"])


def determine_time_ranges_to_process(stream, kvam, process_start, last_timestamp):
    """
    Determine ranges of length VIDEO_LENGTH_IN_SECONDS that we need to copy to S3
    Example: this Lambda function is run at 9:42:12, last video encompasses time range 9:00:00 - 9:10:00
    We need to create videos: 9:10:00 - 9:20:00, 9:20:00 - 9:30:00, 9:30:00 - 9:40:00
    Even if it seems that this would result in having duplicates at range ends (e.g. 9:20:00), it does not.
    On the other hand using ranges like 9:10:00 - 9:19:59 might result in data loss.
    To decrease overall time of execution there's a limit of time ranges that can be retrieved in one lambda execution.
    Also, the last_timestamp is limited to retention time, periods out of retention are skipped.
    If current stream is more than 5 ranges behind, we check if there is any data available. If there is no data at all,
    then we skip to the newest
    """
    data_retention_hours = stream['DataRetentionInHours']
    stream_name = stream['StreamName']

    newest_calculated_start_timestamp = process_start - (
      process_start % VIDEO_LENGTH_IN_SECONDS) - 10 * VIDEO_LENGTH_IN_SECONDS

    if last_timestamp is not None:
        effective_start = last_timestamp

        process_start_datetime = datetime.datetime.utcfromtimestamp(process_start)
        min_retention_datetime = process_start_datetime - datetime.timedelta(hours=data_retention_hours)
        min_retention_timestamp = int(min_retention_datetime.timestamp())

        if effective_start < min_retention_timestamp:
            logger.info(
                "Effective start outside of retention period. Overriding to closest to retention period min border")
            effective_start = min_retention_timestamp + VIDEO_LENGTH_IN_SECONDS - (
              min_retention_timestamp % VIDEO_LENGTH_IN_SECONDS)

        if effective_start + 10 * VIDEO_LENGTH_IN_SECONDS < process_start:
            logger.info(
                "Multiple fragments to be fetched. Possible lambda outage. Checking if any data for stream exists")
            available_fragments = kvam.list_fragments(
                StreamName=stream_name,
                MaxResults=1,
                FragmentSelector={
                    'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
                    'TimestampRange': {
                        'StartTimestamp': min_retention_datetime,
                        'EndTimestamp': process_start_datetime
                    }
                }
            )
            if not available_fragments["Fragments"]:
                logger.info(f"No data available for stream={stream_name}. Overriding last_timestamp to None")
                effective_start = newest_calculated_start_timestamp
    else:
        effective_start = newest_calculated_start_timestamp

    time_ranges = []
    i = effective_start
    max_ranges = int(os.environ.get('MAX_TIME_RANGES') or 5)
    range_index = 0
    while i <= process_start - VIDEO_LENGTH_IN_SECONDS and range_index < max_ranges:
        next_i = (i + VIDEO_LENGTH_IN_SECONDS) - ((i + VIDEO_LENGTH_IN_SECONDS) % VIDEO_LENGTH_IN_SECONDS)
        time_ranges.append((i, next_i))
        i = next_i
        range_index += 1

    # add an extra range for new values reference
    time_ranges.append((i, (i + VIDEO_LENGTH_IN_SECONDS) - ((i + VIDEO_LENGTH_IN_SECONDS) % VIDEO_LENGTH_IN_SECONDS)))
    filtered_ranges = []
    for range1, range2 in pairwise(time_ranges):
        real_range = get_min_and_max_timestamps(kvam, stream_name, range1)
        if real_range is None:
            continue
        if get_min_and_max_timestamps(kvam, stream_name, range2) is None:
            continue
        filtered_ranges.append((real_range["min"], real_range["max"]))

    return filtered_ranges


def get_min_and_max_timestamps(kvam, stream_name, range):
    """Returns a map of the smallest and largest timestamps in a list of Kinesis Video Streams fragments.

    Args:
      kvam: A boto3 KinesisVideoMediaClient object.
      stream_name: The name of the Kinesis Video Streams stream.
      range: A tuple of minimum and maximum datetime for the fragments to be returned.

    Returns:
      A map of the smallest and largest timestamps in the fragments, or None if there are no fragments available.
    """

    timestamps = {}
    next_token = ""

    while next_token is not None:
        if next_token == "":
            list_fragments_response = kvam.list_fragments(
                StreamName=stream_name,
                MaxResults=1000,
                FragmentSelector={
                    'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
                    'TimestampRange': {
                        'StartTimestamp': datetime.datetime.utcfromtimestamp(range[0]),
                        'EndTimestamp': datetime.datetime.utcfromtimestamp(range[1])
                    }
                }
            )
        else:
            list_fragments_response = kvam.list_fragments(
                StreamName=stream_name,
                MaxResults=1000,
                NextToken=next_token,
                FragmentSelector={
                    'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
                    'TimestampRange': {
                        'StartTimestamp': datetime.datetime.utcfromtimestamp(range[0]),
                        'EndTimestamp': datetime.datetime.utcfromtimestamp(range[1])
                    }
                }
            )

        # todo: figure out why it shows as never used if that's a while loop
        next_token = list_fragments_response.get('NextToken')
        fragments = list_fragments_response.get('Fragments')

        if not fragments:
            return None

        for fragment in fragments:
            producer_datetime_start = fragment['ProducerTimestamp']
            producer_datetime_end = producer_datetime_start + datetime.timedelta(
                milliseconds=fragment["FragmentLengthInMilliseconds"])
            timestamp_utc_start = int(producer_datetime_start.astimezone(tz=datetime.timezone.utc).timestamp())
            timestamp_utc_end = int(producer_datetime_end.astimezone(tz=datetime.timezone.utc).timestamp())
            if timestamps.get('min') is None or timestamp_utc_start < timestamps['min']:
                timestamps['min'] = timestamp_utc_start
            if timestamps.get('max') is None or timestamp_utc_end > timestamps['max']:
                timestamps['max'] = timestamp_utc_end

        if not timestamps:
            return None

        return timestamps


def fetch_and_save_clip(stream, kvam, clip_start_time, clip_end_time):
    """
    GetClip API has a limitation of 1 rps for given stream.
    Following sleep serves as throttling mechanism and will be executed
    ONLY if fetching many clips from the same stream. This could happen in a rare case
    when lambda was inactive for some time and needs to catch up with the stream
    """

    for attempt in range(1, MAX_COPY_ATTEMPTS + 1):
        try:
            logger.info(f"Generating video, stream = {stream}, "
                        f"clip_start_time={__format_timestamp(clip_start_time)}, "
                        f"clip_end_time = {__format_timestamp(clip_end_time)}")
            video = fetch_video(stream, kvam, clip_start_time, clip_end_time)
            key = generate_s3_video_key(stream, clip_start_time)
            index = build_video_index(stream, key, clip_start_time, clip_end_time)
            put_stream_video(key, video)
            send_stream_index(index, f"s3://{BUCKET_NAME}/{key}")
            put_stream_last_processing_time(stream, str(clip_end_time))
            return
        except kvam.exceptions.ClientLimitExceededException as e:
            logger.info(f"Request limit exceeded, attempt = {attempt}: {str(e)}")
            time.sleep(1.0)
        except Exception as e:
            logger.info(f"Uncaught Error occured: {e}")

    raise Exception("Request limit exceeded")


def fetch_video(stream, kvam, clip_start_time, clip_end_time):
    clip = kvam.get_clip(
        StreamName=stream,
        ClipFragmentSelector={
            'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
            'TimestampRange': {
                'StartTimestamp': f'{clip_start_time}',
                'EndTimestamp': f'{clip_end_time}'
            }
        }
    )
    video = clip["Payload"].read()
    return video


def generate_s3_video_key(stream, timestamp):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    directory = generate_s3_key_prefix(stream, dt)
    filename = f"video-{dt.strftime('%H:%M:%S')}.mp4"
    return f"{directory}/{filename}"


def generate_s3_error_key(stream, timestamp):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    directory = generate_s3_key_prefix(stream, dt)
    filename = f"error-{dt.strftime('%H:%M:%S')}.txt"
    return f"{directory}/{filename}"


def generate_s3_key_prefix(stream, dt):
    return f"stream={stream}/year={dt.year}/month={dt.month}/day={dt.day}/hour={dt.hour}"


def get_stream_last_processing_time(stream):
    try:
        key = f"{LAST_PROCESSING_TIMESTAMPS_PREFIX}/{stream}.txt"
        data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content = data['Body'].read().decode("UTF-8").strip()
        return int(content)
    except s3.exceptions.NoSuchKey as e:
        logger.info(f"No key found in S3 for stream '{stream}', assuming it's a new stream")
        return None
    except Exception as e:
        raise Exception(
            f"Could not fetch last processing timestamp for stream '{stream}', {type(e)}: {str(e)}") from e


def put_stream_video(key, content):
    if DRY_RUN:
        return
    store_object_in_s3(key, content, "media/mp4")


def put_stream_last_processing_time(stream, content):
    if DRY_RUN:
        return
    store_object_in_s3(f"{LAST_PROCESSING_TIMESTAMPS_PREFIX}/{stream}.txt", content, "plain/text")


def send_stream_index(content, key):
    global INDEX_STREAM_NAME_NEW
    logger.info(f"Sending data to factory  factory = {FACTORY}")
    logger.info(f"Sending data to stream {INDEX_STREAM_NAME}  content = {content}")
    put_response = kc.put_record(StreamName=INDEX_STREAM_NAME, Data=json.dumps(content), PartitionKey=key)
    logger.info(f"Data sended response {put_response}")


def put_stream_processing_error(key, content):
    if DRY_RUN:
        return
    store_object_in_s3(f"{PROCESSING_ERRORS_PREFIX}/{key}", content, "plain/text")


def store_index_in_s3(key, content, content_type):
    if DRY_RUN:
        return
    s3.put_object(
        Body=content,
        Bucket=INDEX_BUCKET_NAME,
        Key=key,
        ContentType=content_type
    )


def store_object_in_s3(key, content, content_type):
    if DRY_RUN:
        return
    s3.put_object(
        Body=content,
        Bucket=BUCKET_NAME,
        Key=key,
        ContentType=content_type
    )


def __format_timestamp(timestamp):
    return f"{datetime.datetime.utcfromtimestamp(timestamp).isoformat()}Z"


def build_video_index(stream, key, clip_start_time, clip_end_time):
    currentTime = datetime.datetime.now(tz=datetime.timezone.utc)
    clip_start_datetime = datetime.datetime.utcfromtimestamp(clip_start_time)
    clip_end_datetime = datetime.datetime.utcfromtimestamp(clip_end_time)

    logger.info(f"Generating video index, stream = {stream}, "
                f"current timestamp={(currentTime)}, "
                f"clip_start_time = {clip_start_datetime}, "
                f"clip_end_time = {clip_end_datetime}")

    return {
        "dataPointId": stream,
        "value": key,
        "receivedAt": transform_date_to_athena_compliant_format(currentTime),
        "takenAt": transform_date_to_athena_compliant_format(clip_start_datetime),
        "postedAt": transform_date_to_athena_compliant_format(currentTime),
        "takenAtEnd": transform_date_to_athena_compliant_format(clip_end_datetime),
        "year": str(currentTime.year),
        "month": str(currentTime.month),
        "day": str(currentTime.day),
        "hour": currentTime.strftime("%H")
    }


def transform_date_to_athena_compliant_format(dt):
    if dt is None:
        return None
    date_with_6_milli_digits = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    return f"{date_with_6_milli_digits[:-3]}"


def pairwise(iterable):
    """Iterates over the pairs of elements in an iterable.

    Args:
      iterable: An iterable of elements.

    Yields:
      A pair of elements from the iterable.
    """

    a, b = itertools.tee(iterable)
    next(b, None)
    for a, b in zip(a, b):
        yield a, b
