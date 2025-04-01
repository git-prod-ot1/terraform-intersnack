#!/bin/bash

# Variables - replace ACCOUNT_ID with your AWS account ID
ACCOUNT_ID="490004635651"
BUCKET_NAME="iscf-terraform-$(date +%s)" # Starts with iscf-terraform + timestamp suffix
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/tf-exec"

echo "creating a bucket"
# Create the S3 bucket
aws s3api create-bucket \
  --bucket "${BUCKET_NAME}" \
  --region eu-central-1 \
  --create-bucket-configuration LocationConstraint=eu-central-1



echo "enabling versioning"
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket "${BUCKET_NAME}" \
  --versioning-configuration Status=Enabled

# Block all public access
aws s3api put-public-access-block \
  --bucket "${BUCKET_NAME}" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Apply bucket policy with separate dev and prod workspace permissions
aws s3api put-bucket-policy --bucket "${BUCKET_NAME}" --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "'${ROLE_ARN}'"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::'"${BUCKET_NAME}"'",
        "arn:aws:s3:::'"${BUCKET_NAME}"'/dev/*"
      ]
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "'${ROLE_ARN}'"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::'${BUCKET_NAME}'",
        "arn:aws:s3:::'${BUCKET_NAME}'/prod/*"
      ]
    }
  ]
}'

# Enable server-side encryption
aws s3api put-bucket-encryption \
  --bucket ${BUCKET_NAME} \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'

echo "Bucket created: ${BUCKET_NAME}"
echo "Role ARN: ${ROLE_ARN}"
