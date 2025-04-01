import base64
import json

from encodings.base64_codec import base64_decode, base64_encode

from dotenv import load_dotenv

load_dotenv(".test.env")

# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE


from main import lambda_handler


class DummyContext:
    def get_remaining_time_in_millis(self):
        return 30000


if __name__ == "__main__":
    event = {
        "invocationId": "8dd437b9-1d6d-4ee2-8f14-be56a11aaee2",
        "sourceKinesisStreamArn": "arn:aws:kinesis:eu-central-1:596966240641:stream/dev_mixes_messages_data_stream",
        "deliveryStreamArn": "arn:aws:firehose:eu-central-1:596966240641:deliverystream/dev_mixed_messages",
        "region": "eu-central-1",
        "records": [
            {
                "recordId": "49615659390235360198692340333316747709505627667520552962000000",
                "approximateArrivalTimestamp": 1613741931873,
                "data": base64.b64encode(
                    json.dumps(
                        {"data":{"dataPointId":"door","takenAt":"2024-10-17T10:39:25Z","postedAt":"2024-10-17T10:39:25.934Z","deviceid":"A8:46:9D:1A:D4:01","additionaldata":"door entry","modelVersion":"0.1.0","configurationModelVersion":"0.1.0","timestream":True,"factoryid":"sweden00002"},"clientid":"dev_sw_sweden00002_v2_0001"}
                    ).encode("utf-8")
                ),
                "kinesisRecordMetadata": {
                    "sequenceNumber": "49615659390235360198692340333316747709505627667520552962",
                    "subsequenceNumber": 0,
                    "partitionKey": "da5f2a9b-672d-44ab-8920-3532938e6cf0",
                    "shardId": "shardId-000000000000",
                    "approximateArrivalTimestamp": 1613741931873,
                },
            }
        ],
    }

    print(lambda_handler(event, None))
