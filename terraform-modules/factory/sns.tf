data "aws_iam_policy_document" "sns" {

  statement {
    sid = "Allow publish to SNS for AWS Principal"

    effect = "Allow"

    actions = [
      "SNS:Publish",
    ]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      aws_sns_topic.factory.arn,
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceOwner"
      values   = [var.aws_user_id]
    }
  }

  statement {
    sid = "Allow SNS Publish for S3 Amazon Service"

    effect = "Allow"

    actions = [
      "SNS:Publish",
    ]

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    resources = [
      aws_sns_topic.factory.arn,
    ]
  }
}


resource "aws_sns_topic" "factory" {
  name              = "${local.name_prefix}_sns"
  kms_master_key_id = "alias/${var.company_namespace}/cloudwatch-sns"
  tags              = local.tags.default
}

resource "aws_sns_topic_policy" "default" {
  arn    = aws_sns_topic.factory.arn
  policy = data.aws_iam_policy_document.sns.json
}

resource "aws_sns_topic_subscription" "this" {
  for_each  = toset(var.sns_alarms_recipients)
  protocol  = "email"
  endpoint  = each.value
  topic_arn = aws_sns_topic.factory.arn
}

