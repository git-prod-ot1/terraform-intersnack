locals {
  default_table_name = "${local.company_name_prefix}_${var.unit_name}"
}

module "kinesis2timestream" {
  source = "../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  function_name_suffix = "kinesis2timestream"
  source_dir           = "${path.module}/lambda/kinesis2timestream"
  iam_role             = aws_iam_role.lambda
  timeout              = 128
  memory_size          = 256
  environment = {
    STAGE   = terraform.workspace
    FACTORY = var.timestream_dimension

    TIMESTREAM_DB            = local.timestream_db_name
    TIMESTREAM_TABLE_DEFAULT = var.default_table_name_override == null ? local.table_prefix : var.default_table_name_override
    TIMESTREAM_TABLE_PREFIX    = local.table_prefix
    TIMESTREAM_TABLE_SUFFIX    = var.table_suffix
    TIMESTREAM_PARTITION_FIELD = var.timestream_partition_field

    BATCH_SIZE    = var.timestream_write_batch_size
    ERRORS_BUCKET = local.errors_bucket_name
    INFER_TYPES   = var.infer_types
  }
}

resource "aws_lambda_event_source_mapping" "kinesis2timestream" {
  event_source_arn                   = var.kinesis_stream.arn
  function_name                      = module.kinesis2timestream.aws_lambda_function.arn
  batch_size                         = var.lambda_trigger_batch_size
  maximum_batching_window_in_seconds = var.lambda_trigger_batch_window
  starting_position                  = "LATEST"
  parallelization_factor             = 8
  maximum_record_age_in_seconds      = 60
  queues = []
  topics = []
}
