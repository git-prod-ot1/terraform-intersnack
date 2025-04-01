locals {
  tables_arn = values({ for p in sort(keys(aws_timestreamwrite_table.this)) : p => aws_timestreamwrite_table.this[p].arn })
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_policy" "read_from_kinesis" {
  name   = "${local.name_prefix}_read_kinesis"
  policy = jsonencode(
  {
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Action" : [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListShards",
          "kinesis:ListStreams"
        ],
        "Resource" : [
          var.kinesis_stream.arn
        ]
      }
    ]
  }
  )
  tags = local.tags.default
}

resource "aws_iam_policy" "write_to_timestream" {
  name   = "${local.name_prefix}_write_timestream"
  policy = jsonencode(
  {
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "timestream:WriteRecords"
        ],
        "Resource" : local.tables_arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "timestream:DescribeEndpoints"
        ],
        "Resource" : "*"
      }
    ]
  }
  )
  tags = local.tags.default
}

resource "aws_iam_role" "lambda" {
  name = "${local.name_prefix}_lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags = local.tags.default
}

resource "aws_iam_role_policy_attachment" "error_action_for_lambda" {
  policy_arn = aws_iam_policy.error_action_for_lambda.arn
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_policy" "error_action_for_lambda" {
  name   = "${local.name_prefix}_S3AllowPutErrors"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : "s3:PutObject",
          "Resource" : "arn:aws:s3:::${local.errors_bucket_name}/*"
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "cloudwatch_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "read_from_kinesis" {
  policy_arn = aws_iam_policy.read_from_kinesis.arn
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "write_to_timestream" {
  policy_arn = aws_iam_policy.write_to_timestream.arn
  role       = aws_iam_role.lambda.name
}
