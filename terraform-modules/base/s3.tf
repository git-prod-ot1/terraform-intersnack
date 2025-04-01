module "athena_tests" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "athena-tests"
}

module "measurement_samples" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "measurement-samples"
}

resource "aws_s3_bucket_notification" "firehose_error" {
  bucket = module.measurement_samples.aws_s3_bucket.bucket

  topic {
    topic_arn     = local.sns_topic.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "errors/"
  }
}

module "picture_feed" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "picture-feed"
  bucket_lifecycle_configuration = var.picture_feed_s3_lifecycle_configuration
}

module "video_feed" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "video-feed"
  bucket_lifecycle_configuration = var.video_feed_s3_lifecycle_configuration
}


module "video_local_index" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "video-local-index"
}

module "iot_rules_actions_logs" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = "iot-rules-actions-logs"
}

resource "aws_s3_bucket_notification" "iot_rules_actions_logs" {
  bucket = module.iot_rules_actions_logs.aws_s3_bucket.bucket
  topic {
    topic_arn     = local.sns_topic.arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ""
  }
}

# according to: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html

data "aws_elb_service_account" "this" {}

module "alb_logs" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name              = "application-load-balancer-logs"
  bucket_policy_statements = [
    {
      "Effect" : "Allow",
      "Principal" : {
        "AWS" : "arn:aws:iam::${data.aws_elb_service_account.this.id}:root"
      },
      "Action" : "s3:PutObject",
      "Resource" : "${module.alb_logs.aws_s3_bucket.arn}/*"
    }
  ]
}

module "athena_queries_s3" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  bucket_name       = "athena-query-results"
  company_namespace = var.company_namespace
  tags              = var.tags

  bucket_name_override = var.query_output_bucket_name
}



module "errors_bucket" {
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  bucket_name       = "errors"
  tags              = local.tags
}
