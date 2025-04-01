module "kinesis2s3" {
  source = "../kinesis2s3"

  unit_name = var.unit_name

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = var.tags

  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_bucket                = var.measurement_samples_bucket
  transformation_lambda                     = var.transformation_lambda

  glue_schema_columns           = var.glue_schema_columns
  glue_schema_extension_columns = var.glue_schema_extension_columns
  partition_keys                = var.glue_partition_keys

  enable_takenat_partitioning = var.enable_takenat_partitioning
  dynamic_partitioning_prefix = var.dynamic_partitioning_prefix
  firehose_source             = var.firehose_source
  on_demand_mode              = var.on_demand_mode
  glue_partitions_updater     = var.glue_partitions_updater
  factory_partition_override  = var.factory_partition_override
  custom_s3_location          = var.custom_s3_location
  sns_alarms_recipients       = var.sns_alarms_recipients
  partitioning_lambda_version = var.partitioning_lambda_version
  create_dashboard            = false
}
