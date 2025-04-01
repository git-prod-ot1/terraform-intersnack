import copy
import datetime
import logging
import os
import re
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

glue = boto3.client('glue')
session = boto3.Session()
s3 = session.resource('s3')

logger = logging.getLogger("parition_updater")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

STAGE = None
COMPANY_NAMESPACE = None
UNIT_NAME = None
DAYS_DELTA = 7


@dataclass
class TimeConfig:
    start: datetime.date
    end: datetime.date


@dataclass
class InputConfig:
    glue_database: str
    glue_table: str
    s3_bucket: str
    data_prefix: str
    time: TimeConfig


def build_config(event):
    time_el = event.get("time")
    now = datetime.datetime.utcnow()
    if time_el:
        start_str = time_el.get("start")
        end_str = time_el.get("end")
        start = datetime.datetime.fromisoformat(start_str) if start_str else now
        end = datetime.datetime.fromisoformat(end_str) if end_str else now
    else:
        start = now - datetime.timedelta(days=DAYS_DELTA)
        end = now

    # we strip a / from s3_location from the end of it for data_prefix as it's more natural to use
    # separators "separately" in string interpolations instead of relying on it being there
    # however, s3_locations comes from default location in glue, so it's expected to be at the end
    bucket_re = re.compile("^s3://(?P<bucket_name>[^/]+)/(?P<data_prefix>.*)/").match(event["s3_location"])
    bucket_name = bucket_re.group("bucket_name")
    data_prefix = bucket_re.group("data_prefix")
    return InputConfig(
        glue_database=event["glue_database"],
        glue_table=event["glue_table"],
        s3_bucket=bucket_name,
        data_prefix=data_prefix,
        time=TimeConfig(
            start=start,
            end=end
        )
    )


def lambda_handler(event, context):
    try:
        main(event)
    except Exception as e:
        logger.critical(f"Unexpected error happened {{e={e}}}")


def main(event):
    """
    Updates Glue partitions based on current state of S3 and date time
    """

    # print(f"Starting Firehose transformation lambda, event = {event}")
    initialize_env()

    config = build_config(event)

    bucket = s3.Bucket(config.s3_bucket)
    results = bucket.meta.client.list_objects(Bucket=config.s3_bucket, Prefix=f"{config.data_prefix}/", Delimiter='/')

    factory_in_data_prefix = "/factory=" in config.data_prefix
    factory_partitions = []

    # if factory is in data prefix - this part is skipped (factory is not a partition)
    # however if factory is not in data prefix, we need to check if it's in common prefixes
    if not factory_in_data_prefix:
        factory_re = re.compile(".*factory=(?P<factory>[^/]+)/")

        for obj in results["CommonPrefixes"]:
            prefix = obj['Prefix']
            factory_match = factory_re.match(prefix)
            if factory_match:
                factory = factory_match.group("factory")
                factory_partitions.append(factory)

    if not factory_partitions:
        update_partition(config)
        return

    for factory in factory_partitions:
        update_partition(config, factory)


def update_partition(config: InputConfig, factory=None):
    delta = datetime.timedelta(days=1)
    start = config.time.start
    while start <= config.time.end:
        year = start.strftime("%Y")
        month = start.strftime("%m")
        day = start.strftime("%d")
        default_partition_values = [
            {"name": "year", "value": year},
            {"name": "month", "value": month},
            {"name": "day", "value": day}
        ]
        partition_values = default_partition_values if not factory else [
                                                                            {
                                                                                "name": "factory",
                                                                                "value": factory
                                                                            }
                                                                        ] + default_partition_values
        partitions_arr = [p["value"] for p in partition_values]

        partition_exists = current_partition_exists(config.glue_database, config.glue_table, partitions_arr)

        if partition_exists is None:
            return  # handle unexpected error
        if check_for_data_in_s3(config, partition_values) and not partition_exists:
            create_current_partition(config.glue_database, config.glue_table, partition_values)
        start += delta


def initialize_env():
    global STAGE, COMPANY_NAMESPACE, UNIT_NAME
    STAGE = os.environ['STAGE']
    COMPANY_NAMESPACE = os.environ['COMPANY_NAMESPACE']


def check_for_data_in_s3(config, partition_values):
    bucket = s3.Bucket(config.s3_bucket)
    partitions = "/".join([f"{partition['name']}={partition['value']}" for partition in partition_values])
    objects = bucket.objects.filter(Prefix=f"{config.data_prefix}/{partitions}/").limit(1)
    s3_objects_exist = bool([obj for obj in objects])
    print(f"S3_object_exists={s3_objects_exist}")
    return s3_objects_exist


def current_partition_exists(database, table, partition_arr):
    try:
        partition = glue.get_partition(
            DatabaseName=database,
            TableName=table,
            PartitionValues=partition_arr
        )
        print(f"Partition exists {partition_arr}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            print(f"Partition does not exists {partition_arr}")
            return False
        else:
            print(f"Something went wrong, requires attention,e={e}")
            return None


def create_current_partition(database, table, partition_values):
    try:
        print(f"Creating partition {partition_values}")
        table_obj = glue.get_table(
            DatabaseName=database,
            Name=table
        )
        storage_descriptor = table_obj['Table']['StorageDescriptor']
        custom_storage_descriptor = copy.deepcopy(storage_descriptor)
        partitions = "/".join([f"{partition['name']}={partition['value']}" for partition in partition_values])

        custom_storage_descriptor['Location'] = storage_descriptor['Location'] + partitions + '/'
        create_partition_response = glue.create_partition(
            DatabaseName=database,
            TableName=table,
            PartitionInput={
                'Values': [p["value"] for p in partition_values],
                'StorageDescriptor': custom_storage_descriptor
            }
        )
        print(f"Partition created successfully")
    except ClientError as e:
        print(f"Something went wrong, requires attention,e={e}")
