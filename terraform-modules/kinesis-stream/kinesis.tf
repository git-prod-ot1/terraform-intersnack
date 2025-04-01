locals {
  aws_kinesis_stream_data_name = "${local.name_prefix}_data_stream"
}

resource "aws_kinesis_stream" "data" {
  name             = local.aws_kinesis_stream_data_name
  shard_count      = var.on_demand_mode ? null : var.shard_count
  retention_period = 24
  stream_mode_details {
    stream_mode = var.on_demand_mode ? "ON_DEMAND" : "PROVISIONED"
  }
  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_kinesis_stream"], {}),
    try(local.tags.named["aws_kinesis_stream"][local.aws_kinesis_stream_data_name], {})
  )
}
