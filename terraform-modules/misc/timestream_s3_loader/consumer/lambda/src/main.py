import os
import logging
from io import BytesIO

import boto3
import pandas as pd
import pyarrow.orc as orc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")
timestream = boto3.client("timestream-write")

DATABASE_NAME = os.environ["TIMESTREAM_DB"]
TABLE_NAME = os.environ["TIMESTREAM_TABLE"]
MAX_BATCH_SIZE = 100

def handler(event, context):
    try:
        process_message(event)
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise RuntimeError(f"Error processing event: {e}") from e

def process_message(event):
    message = event["Records"][0]["body"]
    data = eval(message)
    bucket_name = data["bucket_name"]
    s3_key = data["s3_key"]
    factory = extract_factory_from_key(s3_key)
    process_orc_file(bucket_name, s3_key, factory)

def process_orc_file(bucket_name, s3_key, factory):
    obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    orc_file = orc.ORCFile(BytesIO(obj["Body"].read()))
    df = orc_file.read().to_pandas()

    # Filter out incorrect values
    df = df.dropna(subset=["value", "datapointid", "takenat"])

    # Define a function to check for invalid strings
    def is_valid_value(x):
        if pd.isna(x):
            return False
        x_str = str(x).strip().lower()
        if x_str in {"", "none", "nan"}:
            return False
        if isinstance(x, str) and len(x) > 2048:
            return False
        return True

    # Apply the filtering function
    df = df[df["value"].apply(is_valid_value)]

    records = []
    for _, row in df.iterrows():
        row["value"] = infer_value_type(row["value"])
        if row["value"] is None:
            continue  # Skip rows with invalid values
        records.append(transform_row_to_timestream(row, factory))
        if len(records) == MAX_BATCH_SIZE:
            write_to_timestream(records)
            records.clear()

    if records:
        write_to_timestream(records)

def infer_value_type(value):
    if pd.isna(value) or str(value).strip().lower() == "nan":
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

def transform_row_to_timestream(row, factory):
    measure_value = row["value"]
    measure_type = get_attribute_type(type(measure_value).__name__)
    dimensions = [{"Name": "factory", "Value": factory}]
    timestamp = int(row["takenat"].timestamp() * 1000)
    return {
        "Time": str(timestamp),
        "MeasureName": row["datapointid"],
        "MeasureValue": str(measure_value),
        "MeasureValueType": measure_type,
        "Dimensions": dimensions,
    }

def get_attribute_type(type):
    types = {"bool": "BOOLEAN", "float": "DOUBLE", "int": "DOUBLE", "string": "VARCHAR"}
    return types.get(type) or "VARCHAR"

def write_to_timestream(records):
    try:
        res = timestream.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME, Records=records)
        logger.info(f"Successfully wrote records: {res}")
    except timestream.exceptions.RejectedRecordsException as err:
        rejected_records = err.response["RejectedRecords"]
        for rr in rejected_records:
            if "The record timestamp is outside the time range" in rr['Reason']:
                return
            if "A record already exists with the same time" in rr['Reason']:
                return
            logger.warning(f"Rejected record={records[rr['RecordIndex']]} reason:{rr['Reason']}")
    except Exception as e:
        logger.error(f"Error sending records to Timestream: {e}, batch={records}")

def extract_factory_from_key(s3_key):
    parts = s3_key.split("/")
    for part in parts:
        if part.startswith("factory="):
            return part.split("=")[-1]
    raise ValueError(f"No factory information found in key: {s3_key}")
