locals {
  create_measurement_bucket  = var.measurement_samples_bucket == null ? 1 : 0
  // this is one hacky solution. For details, please reference this: https://github.com/hashicorp/terraform/issues/22405#issuecomment-625619906
  measurement_samples_bucket = var.measurement_samples_bucket == null ? module.measurement_samples[0].aws_s3_bucket : var.measurement_samples_bucket

}

module "measurement_samples" {
  count  = local.create_measurement_bucket
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  bucket_name          = "measurement-samples"
  bucket_name_override = var.bucket_name_override
}

resource "aws_s3_bucket_notification" "firehose_error" {
  count = local.create_measurement_bucket

  bucket = module.measurement_samples[0].aws_s3_bucket.bucket

  topic {
    topic_arn     = coalesce(var.sns_topic_override, try(aws_sns_topic.this[0], null)).arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "errors/"
  }

}
