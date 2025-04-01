module "iot2s3" {
  source = "../../iot2s3"

  unit_name = var.unit_name

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = local.tags

  factory_partition_override                = var.factory_name
  shard_count                               = var.data_stream_shards
  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = var.measurement_samples_glue_table
  measurement_samples_bucket                = var.measurement_samples_bucket

  glue_partitions_updater = "LAMBDA"
  sns_alarms_recipients   = var.sns_alarms_recipients

  create_dashboard         = false
  iot_error_actions_bucket = var.error_bucket

  iot_rule_sql = <<EOT
      SELECT * as data, clientid() as clientid, '${var.factory_name}_republish' as factoryid
      FROM '${var.republished_data_topic}'
  EOT

  send_client_metrics = false
}
