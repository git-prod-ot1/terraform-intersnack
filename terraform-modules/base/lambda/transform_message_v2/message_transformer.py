import base64
import json
import logging
import sys
import traceback
from datetime import datetime

from metrics_collector import MetricsCollector

logger = logging.getLogger("MessageTransformer")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class MessageTransformer:
    def __init__(self, cloudwatch, company_namespace, invocation_id):
        self.company_namespace = company_namespace
        self.metrics_collector = MetricsCollector(cloudwatch, company_namespace)
        self.invocation_id = invocation_id
        self.partition_keys = None
        self.factory_partition = None

    @classmethod
    def __serialize_to_base64(cls, json_string):
        encoded = base64.b64encode(json_string.encode("UTF-8")).decode("UTF-8")
        return encoded

    @classmethod
    def __format_date_with_milliseconds(cls, posix_timestamp_in_milliseconds):
        dt = datetime.utcfromtimestamp(posix_timestamp_in_milliseconds / 1000)
        return cls.__transform_date_to_athena_compliant_format(dt)

    @classmethod
    def __transform_date_to_athena_compliant_format(cls, dt):
        if dt is None:
            return None
        date_with_6_milli_digits = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"{date_with_6_milli_digits[:-3]}"

    def __transform_list_element(self, sample, approximate_arrival_timestamp, clientid):
        self.metrics_collector.collect_metrics(clientid, sample.get("factoryid"))
        taken_at = datetime.fromisoformat(sample['takenAt'].replace("Z", "+00:00"))
        posted_at = datetime.fromisoformat(sample['postedAt'].replace("Z", "+00:00"))
        received_at = datetime.utcfromtimestamp(int(approximate_arrival_timestamp) / 1000)
        taken_at_end = datetime.fromisoformat(
            sample['takenAtEnd'].replace("Z", "+00:00")) if "takenAtEnd" in sample else None

        factoryid = sample.get('factoryid') or sample.get('factoryId') or None
        if factoryid is not None:
            self.factory_partition = factoryid

        merged_with_additional_fields = {
            **sample,
            "invocationId": self.invocation_id,
            "receivedAt": self.__transform_date_to_athena_compliant_format(received_at),
            "takenAt": self.__transform_date_to_athena_compliant_format(taken_at),
            "postedAt": self.__transform_date_to_athena_compliant_format(posted_at),
            "takenAtEnd": self.__transform_date_to_athena_compliant_format(taken_at_end),
            "year": taken_at.strftime("%Y"),
            "month": taken_at.strftime("%m"),
            "day": taken_at.strftime("%d"),
            "hour": taken_at.strftime("%H")
        }

        if self.partition_keys is None:
            self.partition_keys = {
                'year': taken_at.strftime("%Y"),
                'month': taken_at.strftime("%m"),
                'day': taken_at.strftime("%d"),
            }
            if self.factory_partition:
                self.partition_keys['factoryid'] = self.factory_partition
        else:
            expected_keys = {
                'year': taken_at.strftime("%Y"),
                'month': taken_at.strftime("%m"),
                'day': taken_at.strftime("%d"),
            }
            if self.factory_partition:
                expected_keys['factoryid'] = self.factory_partition

            if self.partition_keys != expected_keys:
                print(
                    f"ERROR: partitionKeys are different within the same record actual={self.partition_keys}, expected={expected_keys}")

        return json.dumps(merged_with_additional_fields, ensure_ascii=False)

    def __transform_list(self, record):
        result = []
        for el in record['data']['data']:
            if not el["value"]:
                logger.info(f"Empty value detected, attempting omit {{datapointid={el['dataPointId']}}}")
                continue
            result.append(
                self.__transform_list_element(el, record['approximateArrivalTimestamp'], record['data']['clientid']))
        return self.__serialize_to_base64("".join(result))

    def transform_encoded_records(self, encoded):
        decoded = list(map(lambda el: {'data': self.deserialize_from_base64(el['data']), "recordId": el["recordId"],
                                       "approximateArrivalTimestamp": el['approximateArrivalTimestamp']},
                           encoded))
        return [self.transform_record(record) for record in decoded]

    def transform_record(self, record):
        self.partition_keys = None
        try:
            outer_data = record['data']
            if not (isinstance(outer_data['data'], list)):
                outer_data['data'] = [outer_data['data']]

            transformed = self.__transform_list(record)
            if not transformed:
                return {
                    'recordId': record['recordId'],
                    'result': 'ProcessingFailed',
                    'data': record['data']
                }

            return {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': transformed,
                'metadata': {
                    'partitionKeys': self.partition_keys
                }
            }
        except Exception as e:
            print(f"An error occurred while handling a record: {str(e)}", file=sys.stderr)
            traceback.print_exc()
            return {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            }

    def send_metrics(self):
        self.metrics_collector.send_client_metrics()
        self.metrics_collector.send_factory_metrics()

    @staticmethod
    def strip_object_strings(obj):
        if isinstance(obj, str):
            return obj.strip()

        if isinstance(obj, list):
            return [MessageTransformer.strip_object_strings(element) for element in obj]
        if isinstance(obj, dict):
            return {k.strip(): MessageTransformer.strip_object_strings(v) for k, v in obj.items()}
        else:
            return obj

    @staticmethod
    def deserialize_from_base64(base64_string):
        decoded = base64.b64decode(base64_string).decode("UTF-8")
        deserialized = json.loads(decoded)
        stripped = MessageTransformer.strip_object_strings(deserialized)

        return stripped
