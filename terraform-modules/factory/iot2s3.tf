module "iot2s3" {
  source = "../iot2s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = local.tags

  transformation_lambda                     = var.transformation_lambda
  unit_name                                 = var.unit_name
  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = var.measurement_samples_glue_table
  measurement_samples_bucket                = var.measurement_samples_bucket
  no_of_things                              = var.no_of_things
  shard_count                               = var.data_stream_shards
  create_dashboard                          = false
  sns_topic_override                        = aws_sns_topic.factory
  glue_partitions_updater                   = "LAMBDA"
  glue_schema_extension_columns             = var.glue_schema_extension_columns
  enable_takenat_partitioning               = var.enable_takenat_partitioning
  dynamic_partitioning_prefix               = var.dynamic_partitioning_prefix
  on_demand_mode                            = var.on_demand_mode
  iot_error_actions_bucket                  = var.iot_error_actions_bucket
  disable_no_data_alarm_for_client_number   = var.disable_no_data_alarm_for_client_number
  cloudwatch_alarms_evaluation_period       = var.iot2s3_cloudwatch_alarms_config.period
  cloudwatch_alarms_evaluation_periods      = var.iot2s3_cloudwatch_alarms_config.evaluation_periods
  cloudwatch_alarms_datapoints_to_alarm     = var.iot2s3_cloudwatch_alarms_config.datapoints_to_alarm
  partitioning_lambda_version               = var.partitioning_lambda_version

  override_debug_client_creation = true
  allow_wildcard_debug_client    = true
}
