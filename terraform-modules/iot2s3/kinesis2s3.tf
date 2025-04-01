module "kinesis2s3" {
  source = "../kinesis2s3"

  unit_name = var.unit_name

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = local.tags

  shard_count                               = var.shard_count
  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = var.measurement_samples_glue_table
  measurement_samples_bucket                = var.measurement_samples_bucket
  transformation_lambda                     = var.transformation_lambda

  glue_schema_columns           = var.glue_schema_columns
  glue_schema_extension_columns = var.glue_schema_extension_columns
  glue_crawler_cron             = var.glue_crawler_cron
  glue_partitions_updater       = var.glue_partitions_updater

  create_dashboard           = false
  sns_topic_override         = local.sns_topic
  factory_partition_override = var.factory_partition_override

  enable_takenat_partitioning       = var.enable_takenat_partitioning
  dynamic_partitioning_prefix       = var.dynamic_partitioning_prefix
  on_demand_mode                    = var.on_demand_mode
  glue_table_name_override          = var.glue_table_name_override
  bucket_name_override              = var.bucket_name_override
  partitioning_lambda_version       = var.partitioning_lambda_version
  glue_partitions_from_iot_rule_sql = var.glue_partitions_from_iot_rule_sql
  enable_kinesis_data_streams       = var.aggregate_mode ? false : true
  firehose_source                   = var.default_action_destination == "FIREHOSE" ? "DIRECT_PUT" : "KINESIS"
  send_client_metrics               = var.send_client_metrics
  send_factory_metrics              = var.send_factory_metrics
}
