from dotenv import load_dotenv

load_dotenv("./.test.env")
# has to be imported after env
import boto3
from main import lambda_handler

glue = boto3.client("glue")


# ENVIRONMENT HAS TO LOADED BEFORE THE REST OF THE MODULES DUE TO BOTO3 AWS_PROFILE


class DummyContext:
    def get_remaining_time_in_millis(self):
        return 30000


# not really used, just for local run
def delete_partitions(database, table, partitions, batch=25):
    for i in range(0, len(partitions), batch):
        to_delete = [{k: v[k]} for k, v in zip(["Values"] * batch, partitions[i:i + batch])]
        glue.batch_delete_partition(
            DatabaseName=database,
            TableName=table,
            PartitionsToDelete=to_delete)


if __name__ == '__main__':
    database = "dev_plcf_measurement_samples_database"
    table = "sencrop_raw_measurement_samplesdata"
    s3_location = "s3://dev-plcf-sencrop-measurement-samples/data/factory=sencrop_raw/"
    event = {
        "glue_database": database,
        "glue_table": table,
        "s3_location": s3_location,
        # "time": {
        #     "start": "2021-03-01",
        #     "end": "2023-02-01"
        # }
    }
    lambda_handler(event, DummyContext())
