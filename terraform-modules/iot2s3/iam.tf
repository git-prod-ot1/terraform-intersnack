//TODO: REMOVE FULL ACCESS !!! Evaluate to properly restricted access
data "aws_iam_policy" "AWSIoTThingsRegistration_iot" {
  name = "AWSIoTThingsRegistration"
}

data "aws_iam_policy" "AWSIoTLogging_iot" {
  name = "AWSIoTLogging"
}

data "aws_iam_policy" "AWSIoTRuleActions_iot" {
  name = "AWSIoTRuleActions"
}

resource "aws_iam_role" "iot_role" {
  name               = "${local.name_prefix}_iot"
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
  force_detach_policies = true
  managed_policy_arns = concat([
    data.aws_iam_policy.AWSIoTThingsRegistration_iot.arn,
    data.aws_iam_policy.AWSIoTLogging_iot.arn,
    data.aws_iam_policy.AWSIoTRuleActions_iot.arn
  ],
        var.default_action_destination == "KINESIS" ?
        [] : aws_iam_policy.firehose_put_record_iot[0].arn
  )
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

resource "aws_iam_role" "iot_error_actions" {
  name                = "${local.name_prefix}_iot_error_action"
  assume_role_policy  = data.aws_iam_policy_document.iot_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.iot_error_actions.arn
  ]
  force_detach_policies = true
}

resource "aws_iam_policy" "iot_error_actions" {
  name   = "${local.name_prefix}_iot_error_action_policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Action" : "s3:PutObject",
          "Resource" : "${var.iot_error_actions_bucket.arn}/*"
        },
        {
          "Sid": "SQS",
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": data.aws_sqs_queue.iot_errors.arn
        }
      ]
    }
  )
}

resource "aws_iam_policy" "firehose_put_record_iot" {
  count = var.default_action_destination == "FIREHOSE" ? 1 : 0
  name   = "${local.name_prefix}_FirehosePutRecord_iot"
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
