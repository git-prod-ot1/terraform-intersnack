import boto3
import itertools
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Any, List

from botocore.exceptions import ClientError
from botocore.response import StreamingBody

logger = logging.getLogger("VideoStreamDataArchiver")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def build_kinesis_video_archive_media_client(
        stream_name: str, kv
) -> boto3.session.Session.client:
    logger.debug(f"Create new endpoint for stream:{stream_name}")
    endpoint = kv.get_data_endpoint(StreamName=stream_name, APIName="GET_CLIP")
    return boto3.client(
        "kinesis-video-archived-media", endpoint_url=endpoint["DataEndpoint"]
    )


class KinesisVideoEndpoints:
    def __init__(self):
        self.kvams = dict()

    def endpoint(self, name, kv) -> boto3.session.Session.client:
        if name not in self.kvams.keys():
            self.kvams[name] = build_kinesis_video_archive_media_client(name, kv)
        return self.kvams.get(name)


kinesis_video_endpoints_cache = KinesisVideoEndpoints()


@dataclass
class TimeRange:
    start: datetime
    end: datetime


class DynamoDBStreamIndex:
    def __init__(self, factory: str, stream_name: str, current_timestamp: datetime):
        self.factory = factory
        self.stream_name = stream_name
        self.current_timestamp = current_timestamp

    def item(self):
        return {
            "PK": {"S": f"FACTORY#{self.factory}"},
            "SK": {"S": f"STREAM#{self.stream_name}"},
            "current_timestamp": {
                "S": str(
                    {
                        "stream_name": self.stream_name,
                        "index": str(self.current_timestamp.timestamp()),
                    }
                )
            },
        }


class DynamoDBClipData:
    def __init__(
        self,
        stream_name: str,
        time_range: TimeRange,
        video_bucket: str,
        firehose_name: Optional[str] # TODO: optional not needed here, please change within next layer change
    ):
        self.pk = {"S": f"CLIP#{stream_name}"}
        self.sk = {
            "S": f"START#{time_range.start.strftime('%Y.%m.%d-%H:%M:%S.%f')[:-3]}"
        }
        self.video_task = {
            "stream_name": stream_name,
            "time_range": time_range,
            "video_bucket_name": video_bucket,
            "index_firehose_name": firehose_name
        }

    def item(self):
        return {
            "PK": self.pk,
            "SK": self.sk,
            "clip_data": {"S": str(json.dumps(self.video_task, cls=TimeRangeEncoder))},
        }


class TimeRangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TimeRange):
            return {
                "__time_range__": True,
                "start": obj.start.isoformat(),
                "end": obj.end.isoformat(),
            }
        return super().default(obj)


class TimeRangeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__time_range__" in dct:
            return TimeRange(
                start=datetime.fromisoformat(dct["start"]),
                end=datetime.fromisoformat(dct["end"]),
            )
        return dct

class IncorrectTimeRange(Exception):
    pass

class NoNewVideo(Exception):
    pass


class VideoToShort(Exception):
    pass


class VideoStreamDataArchiver:
    def __init__(self, s3=None, kv=None, kc=None, firehose=None, dynamodb=None, sqs=None):
        global kinesis_video_endpoints_cache
        logger.info("Initializing clients!")
        self.video_max_length_in_seconds = int(
            os.environ.get("VIDEO_LENGTH_IN_SECONDS") or 90
        )
        self.max_list_attempts = int(os.environ.get("MAX_LIST_ATTEMPTS") or 5)
        self.bucket_name = os.environ.get("BUCKET_NAME")
        self.company_namespace = os.environ.get("COMPANY_NAMESPACE")
        self.index_firehose_name = os.environ.get("INDEX_FIREHOSE_NAME")
        self.process_wait_seconds = int(os.environ.get("PROCESS_WAIT_SECONDS") or 90)
        self.lambda_timeout_millis = int(os.environ.get("LAMBDA_TIMEOUT") or 30000)
        self.factory = os.environ.get("FACTORY")
        self.stage = os.environ["STAGE"]
        self.dynamodb_table = os.environ.get("DYNAMODB_TABLE")
        self.queue_url = os.environ.get("QUEUE_URL")
        self.fragments_gap_allowed_millis = int(
            os.environ.get("FRAGMENTS_GAP_ALLOWED_MILLIS") or 100
        )
        self.custom_video_prefix =  os.environ.get("CUSTOM_VIDEO_PREFIX")

        self.s3 = s3 if s3 else boto3.client("s3")
        self.kv = kv if kv else boto3.client("kinesisvideo")
        self.firehose = firehose if firehose else boto3.client("firehose")
        self.dynamodb = dynamodb if dynamodb else boto3.client("dynamodb")
        self.sqs = sqs if sqs else boto3.client("sqs")

        self.last_processed_times = None
        self.current_video_fragments = None

    def __get_factory_last_processed_indexes(self, streams) -> datetime:
        last_timestamps_keys = [
            {
                "PK": {"S": f"FACTORY#{self.factory}"},
                "SK": {"S": f"STREAM#{stream['StreamName']}"},
            }
            for stream in streams
        ]
        logger.debug(
            f"Dynamodb last processed timestamps keys: {last_timestamps_keys}, table: {self.dynamodb_table}"
        )
        raw_db_last_indexes = self.dynamodb.batch_get_item(
            RequestItems={self.dynamodb_table: {"Keys": last_timestamps_keys}}
        )
        logger.debug(f"Dynamodb response: {raw_db_last_indexes}")
        parsed_db_response = [
            json.loads(index["current_timestamp"]["S"].replace("'", '"'))
            for index in raw_db_last_indexes["Responses"][self.dynamodb_table]
        ]

        last_processed_datetimes = {
            item["stream_name"]: datetime.fromtimestamp(
                float(item["index"]), tz=timezone.utc
            )
            for item in parsed_db_response
        }

        logger.debug(f"Last process timestamps:{last_processed_datetimes}")
        return last_processed_datetimes

    def process_streams(self, event, context):
        time_str = event["time"].replace("Z", "+00:00")
        process_start = datetime.fromisoformat(time_str)
        streams = self.__fetch_streams_list()
        logger.debug(f"Endpoints in cache: {kinesis_video_endpoints_cache.kvams.keys()}")
        if not streams:
            logger.info(f"No active streams exiting normally.")
            return

        try:
            self.last_processed_times = self.__get_factory_last_processed_indexes(
                streams
            )
        except Exception as e:
            logger.error(
                f"Exception during dynamo last processed times call: {e}", exc_info=True
            )
            return

        for stream in [s for s in streams]:
            while True:
                if context.get_remaining_time_in_millis() < self.lambda_timeout_millis:
                    logger.info("No time left. Exiting normally.")
                    return
                try:
                    self.__process_stream(stream, process_start)
                except NoNewVideo:
                    logger.info(
                        f"No new video for {stream['StreamName']} at: {process_start}."
                    )
                    self.current_video_fragments = None
                    break
                except IncorrectTimeRange:
                    logger.warning(
						f"The given timerange is incorrect for {stream['StreamName']} at: {process_start}."
						"Possible reason is stream created after start of the process."
					)
                    self.current_video_fragments = None
                    break
                except Exception as e:
                    logger.error(
						f"Cannot process {stream['StreamName']}, exception: {e}",
						exc_info=True,
                    )
                    self.current_video_fragments = None
                    break
        logger.debug(f"Ends.")

    def __process_stream(
        self,
        stream: Dict[str, Any],
        process_start: datetime,
    ):
        last_fragment_end_time = self.last_processed_times.get(stream["StreamName"])
        logger.info(
            f"Processing stream: {stream['StreamName']} from last timestamp:{last_fragment_end_time}"
        )
        if last_fragment_end_time and (
            process_start - last_fragment_end_time
            <= timedelta(seconds=self.process_wait_seconds)
        ):
            # if last fragment was processed less than process_wait_seconds ago, we don't want to process yet
            raise NoNewVideo
        time_range = create_scan_time_range(
            stream["DataRetentionInHours"],
            process_start,
            stream["CreationTime"],
            last_fragment_end_time,
        )
        if not self.current_video_fragments:
            self.current_video_fragments = self.__get_all_video_fragments(
                stream["StreamName"], time_range, last_fragment_end_time
            )

        consistent_video_range = (
            self.__take_first_continuous_range_and_remove_its_fragments()
        )
        if consistent_video_range.end == consistent_video_range.start:
            logger.warning(
                f"Dropping 0 length video clip for stream:{stream['StreamName']} start time:{consistent_video_range.start}"
            )
            if consistent_video_range.end > last_fragment_end_time:
                logger.info(
                    f"Move last processed timestamp to end of zero length video"
                )
                self.__put_stream_last_processing_time(
                    stream["StreamName"], consistent_video_range.end
                )
        else:
            self.__send_video_clip_data_to_be_processed(
                stream["StreamName"], consistent_video_range
            )

    def __fetch_streams_list(self) -> list[str]:
        streams_info = self.kv.list_streams(MaxResults=1000)["StreamInfoList"]
        logger.debug(f"Active streams StreamInfoList: {streams_info}")
        streams = [
            stream
            for stream in streams_info
            if stream["StreamName"].startswith(
                f"{self.stage}_{self.company_namespace}_{self.factory}"
            )
        ]
        if self.custom_video_prefix:
            streams.extend(self.__filter_by_prefix(streams_info, self.custom_video_prefix))
        logger.info(f"Current factory streams info: {streams}")
        return streams

    def __filter_by_prefix(self, all_streams, prefix: str):
        return [stream for stream in all_streams if
				stream["StreamName"].startswith(prefix)]


    def __get_all_video_fragments(
        self, stream_name: str, time_range: TimeRange, last_timestamp: datetime
    ) -> List[Dict[str, Any]]:
        next_token = None
        video_fragments = []
        while True:
            video_fragments_response = self.__get_all_video_fragments_on_video_stream(
                time_range, stream_name, next_token=next_token
            )
            next_token = video_fragments_response.get("NextToken") or None

            video_fragments.extend(video_fragments_response.get("Fragments") or [])
            if not next_token:
                break

        if last_timestamp:
            video_fragments = list(
                filter(
                    lambda fragment: (
                        fragment.get("ProducerTimestamp") >= last_timestamp
                        and fragment.get("FragmentLengthInMilliseconds") > 0
                    ),
                    video_fragments,
                )
            )
        else:
            video_fragments = list(
                filter(
                    lambda fragment: (fragment.get("FragmentLengthInMilliseconds") > 0),
                    video_fragments,
                )
            )

        if len(video_fragments) < 1:
            raise NoNewVideo

        return sorted(
            video_fragments, key=lambda fragment: fragment.get("ProducerTimestamp")
        )

    def __take_first_continuous_range_and_remove_its_fragments(self) -> TimeRange:
        """
        Finds continuous video by comparing gaps between fragments.
        Returns a range of start and end time
        """
        logger.debug("Find first continuous video")

        first_fragment = self.current_video_fragments[0]

        initial_start = first_fragment.get("ProducerTimestamp")
        acc_length = first_fragment.get("FragmentLengthInMilliseconds")
        acc_end = first_fragment.get("ProducerTimestamp") + timedelta(
            milliseconds=acc_length
        )

        for vf1, vf2 in pairwise(self.current_video_fragments):
            next_length = vf2["FragmentLengthInMilliseconds"]
            if acc_length + next_length >= self.video_max_length_in_seconds * 1000:
                # we have reached max video length
                logger.debug(f"Break caused by length {acc_length + next_length}")
                break

            if not self.__are_fragments_continuous(vf1, vf2):
                break

            acc_length += next_length
            acc_end = vf2["ProducerTimestamp"] + timedelta(milliseconds=next_length)

        logger.info(
            f"Continuous video found - start:{initial_start}, end:{acc_end}, length:{acc_length}"
        )

        # remove video fragments contained in range
        result = TimeRange(start=initial_start, end=acc_end)
        self.__remove_fragments_contained_in_range(result)
        return result

    def __remove_fragments_contained_in_range(self, time_range: TimeRange):
        self.current_video_fragments = [
            fragment
            for fragment in self.current_video_fragments
            if fragment.get("ProducerTimestamp") > time_range.end
        ]

    def __are_fragments_continuous(self, previous_f, next_f) -> bool:
        next_start_timestamp = next_f.get("ProducerTimestamp")
        previous_start_timestamp = previous_f.get("ProducerTimestamp")
        previous_length = previous_f.get("FragmentLengthInMilliseconds")

        diff = next_start_timestamp - (
            previous_start_timestamp + timedelta(milliseconds=previous_length)
        )

        result = diff <= timedelta(milliseconds=self.fragments_gap_allowed_millis)
        if not result:
            logger.debug(f"Break by diff of {diff}")
        return result

    def __get_all_video_fragments_on_video_stream(
        self,
        time_range: TimeRange,
        stream_name: str,
        max_result=1000,
        next_token=None,
    ) -> dict:
        # todo: create util retry on exception
        for attempt in range(1, self.max_list_attempts + 1):
            exp_backoff = 0.2
            try:
                client = kinesis_video_endpoints_cache.endpoint(stream_name, self.kv)
                if next_token:
                    return client.list_fragments(
                        StreamName=stream_name,
                        MaxResults=max_result,
                        NextToken=next_token,
                        FragmentSelector={
                            "FragmentSelectorType": "PRODUCER_TIMESTAMP",
                            "TimestampRange": {
                                "StartTimestamp": time_range.start,
                                "EndTimestamp": time_range.end,
                            },
                        },
                    )
                else:
                    return client.list_fragments(
                        StreamName=stream_name,
                        MaxResults=max_result,
                        FragmentSelector={
                            "FragmentSelectorType": "PRODUCER_TIMESTAMP",
                            "TimestampRange": {
                                "StartTimestamp": time_range.start,
                                "EndTimestamp": time_range.end,
                            },
                        },
                    )

            # todo: fix ugly exception with possible fixed imported one
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    logger.warning(
                        f"Requested stream has been removed. Cannot get any information, request omitted for stream name: {stream_name}"
                    )
                    return None
                elif e.response['Error']['Code'] == 'ClientLimitExceededException':
                    logger.warning(
                        f"Request list_fragments limit exceeded, attempt = {attempt}: {str(e)}"
                    )
                    time.sleep(exp_backoff)
                    exp_backoff *= 2
                else:
                    logger.error(f"Exception occurred while trying to get list_fragments: {e}", exc_info=True)
                    raise e
            except Exception as e:
                logger.error(f"list_fragments exception occurred: {e}", exc_info=True)
                raise e

        raise Exception("Request limit exceeded for list_fragments")


    def __send_video_clip_data_to_be_processed(
        self, stream_name: str, time_range: TimeRange
    ):
        self.__put_stream_last_processing_time(stream_name, time_range.end)

        dynamo_clip_data = DynamoDBClipData(
            stream_name=stream_name,
            time_range=time_range,
            video_bucket=self.bucket_name,
            firehose_name=self.index_firehose_name
        )

        self.dynamodb.put_item(
            TableName=self.dynamodb_table,
            Item=dynamo_clip_data.item(),
        )

        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=str({"PK": dynamo_clip_data.pk, "SK": dynamo_clip_data.sk}),
        )
        logger.info(
            f"Message for video stream : {stream_name} time range: {time_range} send"
        )

    def __put_stream_last_processing_time(
        self, stream_name: str, new_current_timestamp: datetime
    ):
        if self.last_processed_times.get(stream_name):
            self.dynamodb.put_item(
                TableName=self.dynamodb_table,
                Item=DynamoDBStreamIndex(
                    stream_name=stream_name,
                    factory=self.factory,
                    current_timestamp=new_current_timestamp,
                ).item(),
                #  enforce sequential processing
                ConditionExpression="current_timestamp = :previous_timestamp_data",
                ExpressionAttributeValues={
                    ":previous_timestamp_data": {
                        "S": str(
                            {
                                "stream_name": stream_name,
                                "index": str(
                                    self.last_processed_times.get(
                                        stream_name
                                    ).timestamp()
                                ),
                            }
                        )
                    }
                },
            )
        else:
            self.dynamodb.put_item(
                TableName=self.dynamodb_table,
                Item=DynamoDBStreamIndex(
                    stream_name=stream_name,
                    factory=self.factory,
                    current_timestamp=new_current_timestamp,
                ).item(),
                #  enforce sequential processing
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )

        #  update in memory timestamps
        self.last_processed_times[stream_name] = new_current_timestamp
        logger.info(
            f"New current stream:{stream_name} process timestamp: {new_current_timestamp}"
        )

    def __process_record(self, record):
        logger.debug(f"Processing record {record}")
        record_data = json.loads(record.replace("'", '"'))
        pk = record_data["PK"]
        sk = record_data["SK"]

        response = self.dynamodb.get_item(
            TableName=self.dynamodb_table, Key={"PK": pk, "SK": sk}
        )

        logger.debug(f"Db response: {response}")
        data = json.loads(
            response["Item"]["clip_data"]["S"].replace("'", '"'), cls=TimeRangeDecoder
        )
        logger.debug(f"Dynamodb task PK={pk}, SK={sk}, data: {data}")

        s3_key = generate_s3_video_key(data["stream_name"], data["time_range"].start)
        datapoint = build_video_datapoint(
            data["stream_name"], s3_key, data["time_range"]
        )

        if data["time_range"].end == data["time_range"].start:
            logger.warning(
                f"Dropping 0 length video clip for stream:{data['stream_name']} start time:{data['time_range'].start}"
            )
            return

        video_data = None
        try:
            video_data = self.__fetch_video(data["stream_name"], data["time_range"])
        except VideoToShort:
            return
        logger.info(f"Video fetched for stream:{data['stream_name']}")

        self.__put_stream_video(s3_key, video_data, data["video_bucket_name"])
        logger.info(f"Video saved to s3: {data['video_bucket_name']}/{s3_key}")

        logger.debug(f"Datapoint: {datapoint}")
        self.__send_stream_datapoint(datapoint, s3_key, data)

    def __fetch_video(self, stream_name: str, time_range: TimeRange) -> StreamingBody:
        """
        According to this: https://boto3.amazonaws.com/v1/
        documentation/api/latest/reference/services/kinesis-video-archived-media/client/get_clip.html
        EndTimestamp is an inclusive value of the START of the last fragment one wants to fetch
        """
        clip = None
        try:
            clip = kinesis_video_endpoints_cache.endpoint(
                stream_name, self.kv
            ).get_clip(
                StreamName=stream_name,
                ClipFragmentSelector={
                    "FragmentSelectorType": "PRODUCER_TIMESTAMP",
                    "TimestampRange": {
                        "StartTimestamp": f"{time_range.start}",
                        "EndTimestamp": f"{time_range.end}",
                    },
                },
            )
            return clip["Payload"].read()
        except ClientError as e:
            if (
                e.response["Error"]["Code"] == "InvalidArgumentException"
                and "StartTimestamp must be before EndTimestamp"
                in e.response["Error"]["Message"]
            ):
                logger.warning(
                    f"Dropping clip due to: InvalidArgumentException for start:{time_range.start}, end: {time_range.end}, diff:{time_range.end - time_range.start}"
                )
                raise VideoToShort
            else:
                raise e

    def __put_stream_video(self, key: str, content: StreamingBody, bucket_name: str):
        logger.debug(f"Sending video to s3 {bucket_name}  key = {key}")
        self.s3.put_object(
            Body=content, Bucket=bucket_name, Key=key, ContentType="media/mp4"
        )

    def __send_stream_datapoint(self, datapoint: dict, key: str, data: str):
        firehose_name = data["index_firehose_name"]
        logger.debug(
            f"Sending data to firehose stream {firehose_name}  content = {datapoint}"
        )
        self.firehose.put_record(
            DeliveryStreamName=firehose_name, Record={'Data': bytes(json.dumps(datapoint, ensure_ascii=False), 'utf-8')}
        )
        logger.info(f"Datapoint send to {firehose_name}")


    def get_clips(self, event, context):
        logger.debug(f"Endpoints in cache: {kinesis_video_endpoints_cache.kvams.keys()}")
        self.__process_record(event["Records"][0]["body"])

#  todo: utils
def transform_date_to_athena_compliant_format(dt: datetime) -> str:
    if dt is None:
        return None
    date_with_6_milli_digits = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return f"{date_with_6_milli_digits[:-3]}"


def __format_timestamp(timestamp) -> str:
    return f"{datetime.utcfromtimestamp(timestamp).isoformat()}Z"


def build_video_datapoint(stream, key, time_range: TimeRange) -> dict:
    current_time = datetime.now(tz=timezone.utc)

    return {
        "dataPointId": stream,
        "value": key,
        "takenAt": transform_date_to_athena_compliant_format(time_range.start),
        "takenAtEnd": transform_date_to_athena_compliant_format(time_range.end),
        "receivedAt": transform_date_to_athena_compliant_format(current_time),
        "postedAt": transform_date_to_athena_compliant_format(current_time),
        "year": time_range.start.strftime("%Y"),
        "month": time_range.start.strftime("%m"),
        "day": time_range.start.strftime("%d"),
        "hour": time_range.start.strftime("%H"),
    }


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


def generate_s3_key_prefix(stream: str, dt: datetime) -> str:
    return (
        f"stream={stream}/year={dt.year}/month={dt.month}/day={dt.day}/hour={dt.hour}"
    )


def generate_s3_video_key(stream: str, dt: datetime) -> str:
    directory = generate_s3_key_prefix(stream, dt)
    filename = f"video-{dt.strftime('%H:%M:%S.%f')[:-3]}.mp4"
    return f"{directory}/{filename}"


def create_scan_time_range(
    data_retention_hours: int,
    process_start: datetime,
    stream_creation_time: datetime,
    last_processing_time: Optional[datetime],
) -> TimeRange:
    """
    This function returns a tuple of start and end time, where we expect any fragments to be. It's based either on last
    processed timestamp or retention period and process (lambda) start
    """
    logger.debug(
        f"Create scan time range from: process_start: {process_start}, "
        f"stream_creation_time: {stream_creation_time}, "
        f"last_processing_time: {last_processing_time}"
    )
    retention_dt = process_start - timedelta(hours=data_retention_hours)
    if not last_processing_time:
        # additional optimisation for newly created streams to avoid API query issues
        scan_start = max(stream_creation_time, retention_dt)
    else:
        scan_start = max(last_processing_time, retention_dt)

    if scan_start >= process_start:
        raise IncorrectTimeRange
    else:
        result = TimeRange(start=scan_start, end=process_start)
        logger.debug(f"Time range scan: {result}")
        return result
