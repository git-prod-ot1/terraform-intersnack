import base64
import json
import logging
import os
import traceback
from datetime import datetime, timezone

from metrics_collector import MetricsCollector

logger = logging.getLogger("MessageTransformer")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class MessageTransformer:
    def __init__(
      self, cloudwatch, company_namespace, invocation_id, topic_partitions=None
    ):
        self.company_namespace = company_namespace
        self.metrics_collector = MetricsCollector(cloudwatch, company_namespace)
        self.invocation_id = invocation_id
        self.partition_keys = None
        self.factory_partition = None
        if topic_partitions:
            self.topic_partitions = topic_partitions.split(",")
        else:
            self.topic_partitions = None

    def __transform_list_element(
      self,
      sample,
      approximate_arrival_timestamp,
      client_id,
      factory_id,
      additional_partitions=None
    ):
        factory_id = factory_id or sample.get("factoryid") or sample.get("factoryId") or None
        self.metrics_collector.collect_metrics(client_id, factory_id)
        taken_at = datetime.fromisoformat(sample["takenAt"].replace("Z", "+00:00"))
        posted_at = datetime.fromisoformat(sample["postedAt"].replace("Z", "+00:00"))
        received_at = datetime.fromtimestamp(
            int(approximate_arrival_timestamp) / 1000,
            tz=timezone.utc
        )
        originated_at = datetime.fromisoformat(sample.get("originatedAt", sample["takenAt"]).replace("Z", "+00:00"))
        taken_at_end = (
            datetime.fromisoformat(sample["takenAtEnd"].replace("Z", "+00:00"))
            if "takenAtEnd" in sample
            else None
        )

        if factory_id is not None:
            self.factory_partition = factory_id

        merged_with_additional_fields = {
            **sample,
            "invocationId": self.invocation_id,
            "receivedAt": self.__transform_date_to_athena_compliant_format(received_at),
            "takenAt": self.__transform_date_to_athena_compliant_format(taken_at),
            "postedAt": self.__transform_date_to_athena_compliant_format(posted_at),
            "takenAtEnd": self.__transform_date_to_athena_compliant_format(
                taken_at_end
            ),
            "originatedAt": self.__transform_date_to_athena_compliant_format(originated_at),
            "year": taken_at.strftime("%Y"),
            "month": taken_at.strftime("%m"),
            "day": taken_at.strftime("%d"),
            "hour": taken_at.strftime("%H"),
        }

        if self.partition_keys is None:
            self.partition_keys = self.create_partition_keys(taken_at, additional_partitions)
        else:
            expected_keys = self.create_partition_keys(taken_at, additional_partitions)

            if self.partition_keys != expected_keys:
                logger.error(
                    f"PartitionKeys are different within the same record actual={self.partition_keys}, expected={expected_keys}"
                )

        return json.dumps(merged_with_additional_fields, ensure_ascii=False)

    def __transform_list(self, record):
        result = []
        for el in record["data"]["data"]:
            if el["value"] == "":
                logger.info(
                    f"Empty value detected, attempting omit {{datapointid={el['dataPointId']}}}"
                )
                continue

            if self.topic_partitions:
                additional_partitions = {}
                for partition in self.topic_partitions:
                    additional_partitions[partition] = record["data"][partition]
            else:
                additional_partitions = None

            approximate_arrival_timestamp = record["approximateArrivalTimestamp"]
            client_id = record["data"].get("clientid") or "undefined"
            factory_id = record["data"].get("factoryid") or el.get("factoryid") or el.get("factoryId") or None
            result.append(
                self.__transform_list_element(
                    el,
                    approximate_arrival_timestamp,
                    client_id,
                    factory_id,
                    additional_partitions,
                )
            )
        return self.__serialize_to_base64("".join(result))

    def transform_encoded_records(self, encoded):
        decoded = list(
            map(
                lambda el: {
                    "data": self.__deserialize_from_base64(el["data"]),
                    "recordId": el["recordId"],
                    "approximateArrivalTimestamp": el["approximateArrivalTimestamp"],
                },
                encoded,
            )
        )
        return [self.transform_record(record) for record in decoded]

    def transform_record(self, record):
        self.partition_keys = None
        self.factory_partition = None
        try:
            outer_data = record["data"]
            if not (isinstance(outer_data["data"], list)):
                outer_data["data"] = [outer_data["data"]]

            transformed = self.__transform_list(record)
            if not transformed:
                logger.info("No values available, rejecting record")
                return {
                    "recordId": record["recordId"],
                    "result": "ProcessingFailed",
                    "data": self.__serialize_to_base64(json.dumps(record["data"])),
                }
            return {
                "recordId": record["recordId"],
                "result": "Ok",
                "data": transformed,
                "metadata": {"partitionKeys": self.partition_keys},
            }
        except Exception as e:
            logger.error(f"An error occurred while handling a record: {str(e)}")
            traceback.print_exc()
            return {
                "recordId": record["recordId"],
                "result": "ProcessingFailed",
                "data": self.__serialize_to_base64(json.dumps(record["data"])),
            }

    def send_metrics(self):
        if os.environ.get("SEND_CLIENT_METRICS", "true") == "true":
            self.metrics_collector.send_client_metrics()
        if os.environ.get("SEND_FACTORY_METRICS", "true") == "true":
            self.metrics_collector.send_factory_metrics()

    def create_partition_keys(self, taken_at, additional_partitions=None):
        partition_keys = {
            "year": taken_at.strftime("%Y"),
            "month": taken_at.strftime("%m"),
            "day": taken_at.strftime("%d"),
        }
        if self.factory_partition:
            partition_keys["factoryid"] = self.factory_partition
        if additional_partitions:
            partition_keys = {**additional_partitions, **partition_keys}
            # partition_keys.update(additional_partitions)
        return partition_keys

    @classmethod
    def __serialize_to_base64(cls, json_string):
        encoded = base64.b64encode(json_string.encode("UTF-8")).decode("UTF-8")
        return encoded

    @classmethod
    def __format_date_with_milliseconds(cls, posix_timestamp_in_milliseconds):
        dt = datetime.fromtimestamp(posix_timestamp_in_milliseconds / 1000, tz=timezone.utc)
        return cls.__transform_date_to_athena_compliant_format(dt)

    @classmethod
    def __transform_date_to_athena_compliant_format(cls, dt):
        if dt is None:
            return None
        date_with_6_milli_digits = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        return f"{date_with_6_milli_digits[:-3]}"

    @classmethod
    def __strip_object_strings(cls, obj):
        if isinstance(obj, str):
            return obj.strip()

        if isinstance(obj, list):
            return [cls.__strip_object_strings(element) for element in obj]
        if isinstance(obj, dict):
            return {k.strip(): cls.__strip_object_strings(v) for k, v in obj.items()}
        else:
            return obj

    @classmethod
    def __deserialize_from_base64(cls, base64_string):
        decoded = base64.b64decode(base64_string).decode("UTF-8")
        deserialized = json.loads(decoded)
        stripped = cls.__strip_object_strings(deserialized)

        return stripped
