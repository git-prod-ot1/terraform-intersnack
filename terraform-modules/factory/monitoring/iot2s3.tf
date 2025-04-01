module "iot2s3" {
  source = "../../../terraform-modules/iot2s3"

  company_namespace = var.company_namespace
  aws_user_id       = var.aws_user_id
  tags              = local.tags

  unit_name = var.unit_name

  no_of_things                              = var.no_of_things
  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = var.measurement_samples_glue_table
  iot_error_actions_bucket                  = var.iot_error_actions_bucket
  enable_takenat_partitioning               = true
  measurement_samples_bucket                = var.measurement_samples_bucket
}


# todo: we should revisit the topic/rule-topics configurations at some point
resource "aws_iot_topic_rule" "subtopic" {
  name        = "${local.name_prefix}_subtopic_rule"
  sql         = "SELECT * as data, clientid() AS clientid FROM '${module.iot2s3.rule_topic}/#'"
  sql_version = "2016-03-23"
  enabled     = true

  kinesis {
    partition_key = "$${newuuid()}"
    role_arn      = module.iot2s3.iot_iam_role.arn
    stream_name   = module.iot2s3.kinesis_data_stream.name
  }

  error_action {
    sqs {
      queue_url  = module.iot2s3.error_queue_url
      role_arn   = module.iot2s3.iot_errors_iam_role.arn
      use_base64 = true
    }
  }
}
