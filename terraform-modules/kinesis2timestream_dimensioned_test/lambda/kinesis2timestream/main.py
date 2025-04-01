import base64
import json
import logging
import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone

import boto3

logger = logging.getLogger("Kinesis2Timestream")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

write_client = boto3.client("timestream-write")
s3 = boto3.client("s3")

BATCH_SIZE: int
STAGE: str
FACTORY: str
TIMESTREAM_DB: str
TIMESTREAM_TABLE_DEFAULT: str
TIMESTREAM_TABLE_PREFIX: str
TIMESTREAM_TABLE_SUFFIX: str

TIMESTREAM_PARTITION_FIELD: str

ERRORS_BUCKET: str
INFER_TYPES: bool

DEFAULT_BATCH_SIZE = 100


def lambda_handler(event, context):
    lambda_start = datetime.now(tz=timezone.utc)
    try:
        init_env()
        records = event["Records"]
        decoded = list(map(decode_record, records))

        all_records = flat_map(decoded)
        all_records_count = len(all_records)

        # filter records with non-compliant measurements
        timestream_records = list(
            filter(discard_non_compliant_measurements, all_records)
        )

        # create dict of "timestream table" -> measurements list (with conversion and sorting)
        dict_table_name2measurements = dict_table_to_measurements(
            timestream_records
        )
        timestream_measurements_count = len(timestream_records)

        send_start = datetime.now(tz=timezone.utc)
        for timestream_table in dict_table_name2measurements.keys():
            for batch in divide_chunks_l(
              dict_table_name2measurements.get(timestream_table), BATCH_SIZE
            ):
                send_timestream(batch, timestream_table)
        end = datetime.now(tz=timezone.utc)
        logger.debug(f"Profiling data: timestream send time:{end - send_start};"
                     f" number of TS records:{timestream_measurements_count} in {BATCH_SIZE}"
                     f" sized batches; whole lambda execution time:{end - lambda_start};"
                     f" omitted measurements count:{all_records_count - timestream_measurements_count};")
    except Exception as e:
        logger.error(f"Something went wrong {e}, event = {event}", exc_info=True)
        backup_error_messages(event, "event_failed")


def dict_table_to_measurements(timestream_records: list[dict]) -> dict[str, list[dict]]:
    """
    Returns a dictionary mapping Timestream table names to lists of measurements as Timestream objects.
    The table name is constructed from measurement.get(TIMESTREAM_PARTITION_FIELD) or a default value.
    Lists are sorted by timestamp for improved timestream write performance.
    """
    sorted_list = sorted(timestream_records, key=lambda m: m["measurement"]["takenAt"])
    result = defaultdict(list)

    for record in sorted_list:
        table_name = get_table_name(record)
        result[table_name].append(convert_to_timestream_obj(record))

    return dict(result)


def get_table_name(record: dict) -> str:
    measurement = record["measurement"]

    table_name = TIMESTREAM_TABLE_DEFAULT  # default - might be overridden later
    return table_name


def decode_record(record):
    # //lambda record: json.loads(base64.b64decode(record["kinesis"]["data"]))["data"]
    record_json = json.loads(base64.b64decode(record["kinesis"]["data"]))
    data = record_json.get("data", {"dataPointId": "empty:record", "timestream": False})

    if type(data) is dict:
        data = [data]

    return [
        {'measurement': item, 'factoryid': record_json.get("factoryid") or item.get("factoryid") or FACTORY} for item in
        data
    ]


def discard_non_compliant_measurements(record: dict) -> bool:
    measurement = record["measurement"]
    if ":" in measurement["dataPointId"]:
        logger.info(
            f"dataPointIds can't contain a colon character, "
            f"discarding message {{datapointId={measurement['dataPointId']}}}"
        )
        return False
    if measurement["value"] is None or measurement["value"] == "":
        logger.info(
            f"value is empty, discarding message {{datapointId={measurement['dataPointId']}}}"
        )
        return False
    if len(str(measurement["value"])) > 2048:
        logger.info(
            f"value is to long, discarding message {{datapointId={measurement['dataPointId']}}}"
        )
        return False
    return True


def init_env():
    global STAGE, FACTORY, \
        TIMESTREAM_DB, TIMESTREAM_TABLE_DEFAULT, \
        TIMESTREAM_TABLE_PREFIX, TIMESTREAM_TABLE_SUFFIX, \
        TIMESTREAM_PARTITION_FIELD, \
        BATCH_SIZE, ERRORS_BUCKET, \
        INFER_TYPES

    FACTORY = os.environ.get("FACTORY") or "None"
    STAGE = os.environ["STAGE"]

    TIMESTREAM_DB = os.environ["TIMESTREAM_DB"]
    TIMESTREAM_TABLE_PREFIX = os.environ["TIMESTREAM_TABLE_PREFIX"]
    TIMESTREAM_TABLE_SUFFIX = os.environ.get("TIMESTREAM_TABLE_SUFFIX")
    TIMESTREAM_TABLE_DEFAULT = os.environ["TIMESTREAM_TABLE_DEFAULT"]

    TIMESTREAM_PARTITION_FIELD = os.environ.get("TIMESTREAM_PARTITION_FIELD") or "deviceName"

    ERRORS_BUCKET = os.environ.get("ERRORS_BUCKET")
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE") or DEFAULT_BATCH_SIZE)
    if BATCH_SIZE > 100:
        BATCH_SIZE = 100
    INFER_TYPES = os.getenv("INFER_TYPES") == "true"


def flat_map(xs):
    ys = []
    for x in xs:
        ys.extend(x)
    return ys


def get_attribute_type(type):
    # DOUBLE | BIGINT | VARCHAR | BOOLEAN | TIMESTAMP | MULTI
    types = {"bool": "BOOLEAN", "float": "DOUBLE", "int": "DOUBLE", "string": "VARCHAR"}
    return types.get(type) or "VARCHAR"


def infer_value_type(value):
    if str(value).strip().lower() == "nan":
        return None

    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            pass
        lower_value = value.strip().lower()
        if lower_value in {"true", "false"}:
            return lower_value == "true"
    return value


def convert_to_timestream_obj(record):
    measurement = record["measurement"]
    taken_at = int(
        datetime.fromisoformat(measurement["takenAt"].replace("Z", "+00:00")).timestamp()
        * 1000
    )
    val = measurement["value"]
    val = infer_value_type(val)
    dim = record["factoryid"]



    return {
        "Dimensions": [
            {"Name": "factory", "Value": dim},
            {"Name": "datapointid", "Value": measurement["dataPointId"]}
        ],
        "MeasureName": "general_data",
        "MeasureValues": [
            {
                "Name": "value",
                "Value": str(val),
                "Type": "VARCHAR"
            },
            {
                "Name": "type",
                "Value": get_attribute_type(type(val).__name__),
                "Type": "VARCHAR"
            }

        ],
        "MeasureValueType": "MULTI",
        "Time": str(taken_at),
    }


def backup_error_messages(message, table: str):
    if ERRORS_BUCKET:
        s3.put_object(
            Body=str(message),
            Bucket=ERRORS_BUCKET,
            Key=f"errors/{FACTORY}-kinesis2timestream/{table}-{uuid.uuid4()}",
            ContentType="text/plain",
        )


def send_timestream(batch: list[dict], timestream_table: str):
    try:
        start = datetime.now(tz=timezone.utc)
        write_client.write_records(
            DatabaseName=TIMESTREAM_DB,
            TableName=timestream_table,
            Records=batch,
            CommonAttributes={},
        )
        end = datetime.now(tz=timezone.utc)
        logger.debug(f"Profiling data: write_client.write_records time: {end - start};"
                     f" TIMESTREAM_DB:{TIMESTREAM_DB}; "
                     f" timestream_table:{timestream_table};")
    except write_client.exceptions.RejectedRecordsException as err:
        rejected_records = err.response["RejectedRecords"]
        logger.error(
            f"RejectedRecords for table:{timestream_table}, number of rejected records: {len(rejected_records)}, Error: {err}")
        for rr in rejected_records:
            logger.error(
                f"Rejected record={batch[rr['RecordIndex']]} reason:{rr['Reason']}"
            )
        backup_error_messages(batch, timestream_table)
    except Exception as e:
        logger.error(f"ERROR send_timestream ex={e}, batch={batch}")
        backup_error_messages(batch, timestream_table)


def divide_chunks_l(l, length):
    # looping till length l
    for i in range(0, len(l), length):
        yield l[i: i + length]
