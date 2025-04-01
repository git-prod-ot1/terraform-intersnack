import boto3
import pyorc
from io import BytesIO

# Configure AWS credentials and S3 client
s3 = boto3.client('s3')

# Define the bucket name and prefix
bucket_name = "prod-encf-measurement-samples"
prefix = "data/factory=stegaurach/year=2024/month=12"

def get_first_orc_file(bucket, prefix):
    try:
        # List objects in the bucket with the given prefix
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response or not response['Contents']:
            print("No files found with the given prefix.")
            return None
        # Return the first file key
        return response['Contents'][0]['Key']
    except Exception as e:
        print(f"Error listing S3 objects: {e}")
        return None

def read_orc_file_from_s3(bucket, key):
    try:
        # Fetch the ORC file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        orc_data = BytesIO(response['Body'].read())

        # Read the ORC file
        reader = pyorc.Reader(orc_data)
        print("ORC File Schema:", reader.schema)
        for row in reader:
            print(row)
    except Exception as e:
        print(f"Error reading ORC file: {e}")

if __name__ == '__main__':
    # Get the first ORC file from the prefix
    first_orc_file = get_first_orc_file(bucket_name, prefix)

    if first_orc_file:
        print(f"Reading ORC file: {first_orc_file}")
        read_orc_file_from_s3(bucket_name, first_orc_file)
    else:
        print("No ORC file found to read.")
