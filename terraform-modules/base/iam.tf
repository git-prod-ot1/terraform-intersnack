resource "aws_iam_account_password_policy" "strict" {
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_symbols                = true
  allow_users_to_change_password = true
}

resource "aws_iam_group" "siiusers" {
  name = "${local.company_name_prefix}_SiiUsers"
}

resource "aws_iam_group" "terraform" {
  name = "${local.company_name_prefix}_Terraform"
}

resource "aws_iam_group" "admins" {
  name = "${local.company_name_prefix}_Admins"
}

resource "aws_iam_group" "remote_cameras" {
  name = "${local.company_name_prefix}_RemoteCameras"
}

resource "aws_iam_group" "ptc" {
  name = "${local.company_name_prefix}_PTC"
}

# todo: draft policy for timestream, needs to be parametrized and use database/tables from fabrics outputs
resource "aws_iam_group_policy" "ptc_timestream" {
  name   = "${local.company_name_prefix}_AllowTimestreamRead"
  group  = aws_iam_group.ptc.name
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "timestream:DescribeDatabase",
            "timestream:ListTables",
            "timestream:Select",
            "timestream:DescribeTable"
          ],
          "Resource" : [
            "arn:aws:timestream:${var.region}:${var.aws_user_id}:database/${local.company_name_prefix}",
            "arn:aws:timestream:${var.region}:${var.aws_user_id}:database/${local.company_name_prefix}/table/*"
          ]
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "timestream:DescribeEndpoints",
            "timestream:ListDatabases",
            "timestream:SelectValues"
          ],
          "Resource" : "*"
        }
      ]
    }
  )
}

resource "aws_iam_group_policy" "ptc_policy" {
  name   = "${local.company_name_prefix}_AllowAthenaAccess_PTC_Policy"
  group  = aws_iam_group.ptc.name
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "athena:StartQueryExecution",
            "athena:GetQueryResultsStream",
            "athena:GetWorkGroup",
            "athena:StopQueryExecution",
            "athena:GetQueryExecution",
            "athena:GetQueryResults",
            "glue:GetPartitions",
            "glue:GetTable",
            "glue:GetDatabase",
            "glue:GetPartition",
            "s3:ListBucket",
            "s3:PutObject",
            "s3:GetObject",
            "s3:GetBucketLocation"
          ],
          "Resource" : [
            "arn:aws:s3:::${module.athena_tests.aws_s3_bucket.bucket}/*",
            "arn:aws:s3:::${module.measurement_samples.aws_s3_bucket.bucket}/*",
            "arn:aws:s3:::${module.athena_tests.aws_s3_bucket.bucket}",
            "arn:aws:s3:::${module.measurement_samples.aws_s3_bucket.bucket}",
            "arn:aws:athena:${var.region}:${var.aws_user_id}:workgroup/primary",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:catalog",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:database/${module.measurement_samplesdata.table.database_name}",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:database/${module.measurement_samplesdata.table.database_name}/*",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:table/${module.measurement_samplesdata.table.database_name}/${module.measurement_samplesdata.table.name}",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:table/${module.measurement_samplesdata.table.database_name}/*"
          ]
        },
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : [
            "glue:GetPartition",
            "glue:GetPartitions",
            "glue:GetTable"
          ],
          "Resource" : [
            "arn:aws:glue:${var.region}:${var.aws_user_id}:catalog",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:database/${module.measurement_samplesdata.table.database_name}",
            "arn:aws:glue:${var.region}:${var.aws_user_id}:table/${module.measurement_samplesdata.table.database_name}/${module.measurement_samplesdata.table.name}"
          ]
        }
      ]
    }
  )
}

resource "aws_iam_group_policy_attachment" "remote_cameras_s3" {
  group      = aws_iam_group.remote_cameras.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_group_policy_attachment" "remote_cameras_kinesis" {
  group      = aws_iam_group.remote_cameras.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonKinesisVideoStreamsFullAccess"
}

resource "aws_iam_group_policy_attachment" "remote_cameras_iot" {
  group      = aws_iam_group.remote_cameras.name
  policy_arn = "arn:aws:iam::aws:policy/AWSIoTFullAccess"
}

module "camera_user" {
  source = "../iam-user"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  user_name = "camera_user"
  policies  = []
}

module "ptc_technical_user" {
  source = "../iam-user"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  user_name = "technical_user"
  policies  = []
}

resource "aws_iam_group_membership" "cameras_group_membership" {
  group = aws_iam_group.remote_cameras.name
  name  = aws_iam_group.remote_cameras.name
  users = [
    module.camera_user.user.name
  ]
}

resource "aws_iam_user_group_membership" "assign_ptc_user_to_ptc_group" {
  groups = [
    aws_iam_group.ptc.name
  ]
  user = module.ptc_technical_user.user.name
}

resource "aws_iam_role" "pliot" {
  name               = "${local.company_name_prefix}_PLIoT"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "iot.amazonaws.com"
          },
          "Action" : "sts:AssumeRole"
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "AWSIoTThingsRegistration" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration"
  role       = aws_iam_role.pliot.name
}

resource "aws_iam_role_policy_attachment" "AWSIoTLogging" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTLogging"
  role       = aws_iam_role.pliot.name
}

resource "aws_iam_role_policy_attachment" "AmazonKinesisFullAccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonKinesisFullAccess"
  role       = aws_iam_role.pliot.name
}

resource "aws_iam_role_policy_attachment" "AWSIoTRuleActions" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions"
  role       = aws_iam_role.pliot.name
}

resource "aws_iam_policy" "iot_put_object_s3" {
  name   = "${local.company_name_prefix}_S3AllowPutObject"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : "s3:PutObject",
          "Resource" : "*"
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "iot_rule_allow_s3" {
  policy_arn = aws_iam_policy.iot_put_object_s3.arn
  role       = aws_iam_role.pliot.name
}

resource "aws_iam_role" "firehose_videostream" {
  name               = "${local.company_name_prefix}_KinesisFireHoseServiceRole-Videostream"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "firehose.amazonaws.com"
          },
          "Action" : "sts:AssumeRole"
        }
      ]
    }
  )
}

resource "aws_iam_policy" "cloudwatch_put_metrics" {
  name   = "${local.company_name_prefix}_CloudWatchAllowPutMetrics"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : "cloudwatch:PutMetricData",
          "Resource" : "*"
        }
      ]
    }
  )
}

resource "aws_iam_policy" "kinesis_put_records" {
  name   = "${local.company_name_prefix}_KinesisPutRecords"
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
          "Resource" : "*"
        }
      ]
    }
  )
}

resource "aws_iam_role" "lambda" {
  name = "${local.company_name_prefix}_AWSLambdaRoleDefault"

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
}

resource "aws_iam_role_policy_attachment" "put_metrics_for_lambda" {
  policy_arn = aws_iam_policy.cloudwatch_put_metrics.arn
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "put_kinesis_records_for_lambda" {
  policy_arn = aws_iam_policy.kinesis_put_records.arn
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "cloudwatch_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "kinesis_video_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonKinesisVideoStreamsReadOnlyAccess"
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "s3_for_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.lambda.name
}


resource "aws_iam_role" "glue_default_role" {
  name               = "${local.company_name_prefix}_AWSGlueServiceRoleDefault"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "glue.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "glue_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
  role       = aws_iam_role.glue_default_role.name
}

resource "aws_iam_role_policy_attachment" "s3_for_glue" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.glue_default_role.name
}

data "aws_iam_policy_document" "iot_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = [
        "iot.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "iot_logs" {
  name                = "${local.name_prefix}_iot_logs"
  assume_role_policy  = data.aws_iam_policy_document.iot_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.iot_logs.arn
  ]
  force_detach_policies = true
}

resource "aws_iam_policy" "iot_logs" {
  name   = "${local.name_prefix}_iot_logs"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "logs:PutMetricFilter",
            "logs:PutRetentionPolicy"
          ],
          "Resource" : [
            "arn:aws:logs:*:${var.aws_user_id}:log-group:*:log-stream:*"
          ]
        }
      ]
    }
  )
}
