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

resource "aws_iam_role" "glue_partitions_lambda" {
  name = "${local.name_prefix}_glue_partitions_lambda"

  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.glue_partitions_lambda.arn,
    data.aws_iam_policy.lambda_default_role.arn
  ]
  tags = local.tags.default
}

resource "aws_iam_policy" "glue_partitions_lambda" {
  name   = "${local.name_prefix}_glue_partitions_lambda"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "glue:GetPartition",
            "glue:CreatePartition",
            "glue:GetTable",
            "s3:ListBucket"
          ],
          "Resource" : [
            # this is not problematic
            "*",
          ]
        }
      ]
    }
  )
}

data "aws_iam_policy" "lambda_default_role" {
  name = "AWSLambdaBasicExecutionRole"
}

