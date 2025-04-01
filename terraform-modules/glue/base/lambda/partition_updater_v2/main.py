import copy
import logging
import os
import re
from dataclasses import dataclass
from datetime import timedelta, datetime

import boto3
from botocore.exceptions import ClientError

glue = boto3.client("glue")
session = boto3.Session()
s3 = session.resource("s3")
s3_client = boto3.client("s3")

logger = logging.getLogger("partition_updater_v2.1")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

STAGE: str
COMPANY_NAMESPACE: str
DAYS_DELTA: int = 7
MAX_S3_LOOKUP_DEPTH: int = 10


@dataclass
class TimeConfig:
    start: datetime
    end: datetime


@dataclass
class InputConfig:
    glue_database: str
    glue_table: str
    s3_bucket: str
    data_prefix: str
    time: TimeConfig


def build_config(event) -> InputConfig:
    time_el = event.get("time")
    now = current_datetime()
    if time_el:
        start_str = time_el.get("start")
        end_str = time_el.get("end")
        start = datetime.fromisoformat(start_str) if start_str else now
        end = datetime.fromisoformat(end_str) if end_str else now
    else:
        start = now - timedelta(days=DAYS_DELTA)
        end = now

    # we strip a / from s3_location from the end of it for data_prefix as it's more natural to use
    # separators "separately" in string interpolations instead of relying on it being there
    # however, s3_locations comes from default location in glue, so it's expected to be at the end
    bucket_re = re.compile("^s3://(?P<bucket_name>[^/]+)/(?P<data_prefix>.*)/").match(
        event["s3_location"]
    )
    bucket_name = bucket_re.group("bucket_name")
    data_prefix = bucket_re.group("data_prefix")
    return InputConfig(
        glue_database=event["glue_database"],
        glue_table=event["glue_table"],
        s3_bucket=bucket_name,
        data_prefix=data_prefix,
        time=TimeConfig(start=start, end=end),
    )


def current_datetime():
    return datetime.utcnow()


def lambda_handler(event, context):  # pragma: no mutate
    try:
        handle_event(event)  # pragma: no mutate
    except Exception as e:
        logger.critical(f"Unexpected error happened {{e={e}}}", exc_info=True)


def handle_event(event):
    """
    Updates Glue partitions based on current state of S3 and date time
    """

    logger.info(f"Starting event: {event}")
    initialize_env()

    config = build_config(event)
    logger.info(f"Config: {config}")

    paths = get_s3_data_files_paths(config.s3_bucket, config.data_prefix, config.time)
    logger.info(f"Paths to check if glue index exists: {paths}")

    for path in paths:
        partitions = partitions_data_from_path(path, config.data_prefix)

        partition_values = [p["value"] for p in partitions]
        if not partition_exists(
            config.glue_database, config.glue_table, partition_values
        ):
            create_partition(config.glue_database, config.glue_table, partitions)


def get_s3_data_files_paths(bucket_name, prefix, time_config: TimeConfig) -> [str]:
    """
    Returns list of s3 paths with data files as candidates for glue index.
    Paths are expected to contain date in format and order: ".../year=x/month=y/day=z/..."
    and are limited with time_config.
    """
    paginator = s3_client.get_paginator("list_objects_v2")
    paths = []

    def find_data_files_from_s3_prefix(ls_prefix=prefix):
        response = paginator.paginate(
            Bucket=bucket_name, Prefix=ls_prefix, Delimiter="/"
        )
        for page in response:
            for common_prefix in page.get("CommonPrefixes", []):

                if critical_depth_reached(common_prefix["Prefix"]):
                    logger.error("Recursive s3 traversing depth limit reached")
                    continue

                if not prefix_in_date(common_prefix["Prefix"], time_config):
                    continue

                if s3_prefix_contains_last_index(common_prefix["Prefix"]):

                    if s3_path_contains_files(bucket_name, common_prefix["Prefix"]):
                        paths.append(common_prefix["Prefix"])
                else:
                    find_data_files_from_s3_prefix(common_prefix["Prefix"])

    find_data_files_from_s3_prefix()

    return paths


def s3_path_contains_files(s3_bucket_name: str, s3_prefix: str) -> bool:
    response = s3_client.list_objects_v2(
        Bucket=s3_bucket_name, Prefix=s3_prefix, Delimiter="/", MaxKeys=1
    )
    return "Contents" in response and len(response["Contents"]) > 0


def s3_prefix_contains_last_index(s3_prefix: str) -> bool:
    return "/day=" in s3_prefix


def critical_depth_reached(s3_prefix: str) -> bool:
    return s3_prefix.count("/") >= MAX_S3_LOOKUP_DEPTH


def prefix_in_date(prefix: str, time_config: TimeConfig) -> bool:
    """
    Returns true if prefix containing date information is not out off TimeConfig bounds.
    """
    day = extract_int_value(prefix, "day")
    month = extract_int_value(prefix, "month")
    year = extract_int_value(prefix, "year")

    if not year:
        return True

    if year and month and day:
        parsed_date = datetime(year=year, month=month, day=day)
        return time_config.start <= parsed_date <= time_config.end
    elif year and month:
        first_month_day = datetime(year=year, month=month, day=1)
        last_month_day = (
            datetime(year=year, month=month + 1, day=1) - timedelta(days=1)
            if month < 12
            else datetime(year, 12, 31)
        )
        return time_config.start <= last_month_day or first_month_day <= time_config.end
    elif year:
        return time_config.start.year <= year <= time_config.end.year
    else:
        logger.error(f"Something wrong with path date parsing on path: {prefix}")


def partitions_data_from_path(path: str, data_prefix: str) -> [dict]:
    segments = path.replace(data_prefix, "").strip("/").split("/")

    # Create the list of dictionaries
    dict_list = []
    for segment in segments:
        name, value = segment.split("=")
        dict_list.append({"name": name, "value": value})

    return dict_list


def partition_exists(database, table, partition_arr):
    try:
        glue.get_partition(
            DatabaseName=database, TableName=table, PartitionValues=partition_arr
        )
        logger.info(f"Partition exists: {partition_arr}")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityNotFoundException":
            logger.info(f"Partition does not exists: {partition_arr}")
            return False
        else:
            logger.error(
                f"Something went wrong, requires attention, e={e}", exc_info=True
            )
            return None


def create_partition(database, table, partition_values):
    try:
        logger.info(f"Creating partition {partition_values} for {table}")
        table_obj = glue.get_table(DatabaseName=database, Name=table)
        storage_descriptor = table_obj["Table"]["StorageDescriptor"]
        custom_storage_descriptor = duplicate_with_custom_location(
            storage_descriptor, partition_values
        )
        glue.create_partition(
            DatabaseName=database,
            TableName=table,
            PartitionInput={
                "Values": [p["value"] for p in partition_values],
                "StorageDescriptor": custom_storage_descriptor,
            },
        )
        logger.info(f"Partition created successfully")
    except ClientError as e:
        logger.error(f"Something went wrong, requires attention,e={e}", exc_info=True)


def duplicate_with_custom_location(storage_descriptor, partition_values):
    custom_storage_descriptor = copy.deepcopy(storage_descriptor)
    partitions = "/".join(
        [f"{partition['name']}={partition['value']}" for partition in partition_values]
    )
    custom_storage_descriptor["Location"] = (
        storage_descriptor["Location"] + partitions + "/"
    )
    return custom_storage_descriptor


def extract_int_value(s: str, keyword: str) -> int or None:
    """
    Extract as int number contained in string in format "keyword=x"
    """
    # Construct the regex pattern dynamically based on the keyword
    pattern = rf"{keyword}=(\d+)"
    # Use regex to find 'keyword=xxxx'
    match = re.search(pattern, s)
    if match:
        # Extract the value
        value = match.group(1)
        return int(value)
    # Return None if keyword is not found or pattern doesn't match
    return None


def initialize_env():
    global STAGE, COMPANY_NAMESPACE
    STAGE = os.environ["STAGE"]
    COMPANY_NAMESPACE = os.environ["COMPANY_NAMESPACE"]
