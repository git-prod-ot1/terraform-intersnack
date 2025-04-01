moved {
  from = aws_cloudwatch_metric_alarm.qoutas_almost_reached
  to   = module.kinesis_stream[0].aws_cloudwatch_metric_alarm.quotas_almost_reached
}

resource "aws_cloudwatch_log_group" "firehose_delivery_stream" {
  name              = "/aws/kinesisfirehose/${local.name_prefix}_delivery_stream"
  retention_in_days = 14
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["/aws/kinesisfirehose/${local.name_prefix}_delivery_stream"], {})
  )
}

resource "aws_cloudwatch_log_stream" "firehose_delivery_stream_s3" {
  name           = "${local.company_name_prefix}_S3Delivery"
  log_group_name = aws_cloudwatch_log_group.firehose_delivery_stream.name
}

