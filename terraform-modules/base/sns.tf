locals {
  create_sns_topic = var.sns_topic == null
  sns_topic        = coalesce(var.sns_topic, aws_sns_topic.this[0])
}

data "aws_iam_policy_document" "sns" {
  count = local.create_sns_topic ? 1 : 0

  statement {
    sid    = "s3"
    effect = "Allow"

    actions = [
      "SNS:Publish",
    ]

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    resources = [
      aws_sns_topic.this[0].arn,
    ]
  }
  statement {
    sid     = "default"
    effect  = "Allow"
    actions = [
      "SNS:Publish"
    ]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    condition {
      test     = "StringEquals"
      values   = [var.aws_user_id]
      variable = "AWS:SourceOwner"
    }
    resources = [
      aws_sns_topic.this[0].arn,
    ]
  }
}

locals {
  aws_sns_topic_name = "${local.name_prefix}_sns"
}

resource "aws_sns_topic" "this" {
  count             = local.create_sns_topic ? 1 : 0
  name              = local.aws_sns_topic_name
  kms_master_key_id = "alias/${var.company_namespace}/cloudwatch-sns"
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_sns_topic"], {}),
    try(local.tags.named["aws_sns_topic"][local.aws_sns_topic_name], {})
  )
}

resource "aws_sns_topic_policy" "default" {
  count  = local.create_sns_topic ? 1 : 0
  arn    = aws_sns_topic.this[0].arn
  policy = data.aws_iam_policy_document.sns[0].json
}

resource "aws_sns_topic_subscription" "this" {
  for_each  = toset(var.sns_alarms_recipients)
  protocol  = "email"
  endpoint  = each.value
  topic_arn = local.sns_topic.arn
}
