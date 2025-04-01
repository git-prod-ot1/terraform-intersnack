data "aws_iam_policy" "lambda_default_role" {
  name = "AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "input_lambda" {
  name = "${local.name_prefix}_AWSLambdaRole"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
  force_detach_policies = true
  managed_policy_arns = concat([
    aws_iam_policy.index_s3_lambda.arn,
    aws_iam_policy.secret_lambda.arn,
    data.aws_iam_policy.lambda_default_role.arn
  ],
    [
        var.firehose_source == "KINESIS"
        ? aws_iam_policy.kinesis_put_record_lambda[0].arn
        : aws_iam_policy.firehose_put_record_lambda[0].arn
    ]
  )
}

resource "aws_iam_policy" "index_s3_lambda" {
  name   = "${local.name_prefix}_S3Index_lambda"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : ["s3:ListBucket", "s3:GetObject", "s3:PutObject"],
          "Effect" : "Allow",
          "Resource" : [
            local.index_bucket.arn,
            "${local.index_bucket.arn}/*"
          ]
        }
      ]
    }
  )
}

resource "aws_iam_policy" "secret_lambda" {
  name   = "${local.name_prefix}_read_secret"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "secretsmanager:GetResourcePolicy",
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
            "secretsmanager:ListSecretVersionIds"
          ],
          "Resource" : [
            "arn:aws:secretsmanager:${var.region}:${var.aws_user_id}:secret:${local.name_prefix}*",
            "arn:aws:secretsmanager:${var.region}:${var.aws_user_id}:secret:${local.name_prefix}",
          ]
        }
      ]
    }
  )
}

resource "aws_iam_policy" "kinesis_put_record_lambda" {
  count = var.firehose_source == "KINESIS" ? 1 : 0
  name   = "${local.name_prefix}_KinesisPutRecord_lambda"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "kinesis:PutRecord",
            "kinesis:PutRecords"
          ],
          "Resource" : module.kinesis2s3.kinesis_data_stream.arn
        }
      ]
    }
  )
}

resource "aws_iam_policy" "firehose_put_record_lambda" {
  count = var.firehose_source == "DIRECT_PUT" ? 1 : 0
  name   = "${local.name_prefix}_FirehosePutRecord_lambda"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "firehose:PutRecord",
            "firehose:PutRecordBatch"
          ],
          "Resource" : module.kinesis2s3.firehose_stream.arn
        }
      ]
    }
  )
}
