#!/bin/bash

# Parameters
REGION="eu-central-1"
TABLE_NAME="dev_plcf_videostreams"
S3_BUCKET="dev-plcf-video-feed"
S3_PREFIX="LAST-PROCESSING-TIMESTAMPS/dev_plcf_ju"
FACTORY_SHORT="ju"
PROFILE="plcf-dev"

# Retrieve files from S3 matching the prefix
file_list=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}" --region "${REGION}" --profile="${PROFILE}" | awk '{print $4}')
count=0

# Process each file
for s3_file in $file_list; do
    # Extract filename without extension
    file_name=$(basename "$s3_file" | cut -f 1 -d '.')

    # Retrieve value from S3 file
    value=$(aws s3 cp "s3://${S3_BUCKET}/LAST-PROCESSING-TIMESTAMPS/${s3_file}" --profile="${PROFILE}" - | tr -d '\n')

    echo "$s3_file value: $value"

    json="{\"PK\": {\"S\": \"FACTORY#"${FACTORY_SHORT}"\"}, \"SK\": {\"S\": \"STREAM#"${file_name}"\"}, \"current_timestamp\": {\"S\": \"{'stream_name': '"${file_name}"', 'index': '"${value}".999'}\"}}"

    echo "Json: $json"
    # Insert item into DynamoDB
    aws dynamodb put-item --profile="${PROFILE}" \
        --table-name "${TABLE_NAME}" \
        --region "${REGION}" \
        --item "${json}"
    ((count++))
done

echo "Processed $count timestamps"
