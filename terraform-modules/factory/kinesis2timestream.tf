locals {
  enable_timestream = contains(var.data_destinations, "TIMESTREAM") ? 1 : 0
}

module "kinesis2timestream" {
  count  = local.enable_timestream
  source = "../kinesis2timestream"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags


  kinesis_stream                = module.iot2s3.kinesis_data_stream
  alarm_sns_topic               = aws_sns_topic.factory
  timestream_db                 = var.base.aws_timestreamwrite_database
  timestream_dimension = var.unit_name //this is factory name in that case
  timestream_table_names        = var.timestream_table_names
  timestream_magnetic_retention = var.timestream_magnetic_retention
  timestream_memory_retention   = var.timestream_memory_retention
  table_skip_prefix             = var.timestream_table_skip_prefix
  table_prefix_override         = var.timestream_table_prefix_override
  default_table_name_override   = var.timestream_default_table_name_override
  errors_bucket_name            = var.errors_bucket_name
  timestream_partition_field    = var.timestream.partition_field
}
