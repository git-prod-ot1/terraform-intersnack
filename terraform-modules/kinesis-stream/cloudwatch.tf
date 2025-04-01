resource "aws_cloudwatch_metric_alarm" "quotas_almost_reached" {
  alarm_actions = [
    var.sns_topic_arn
  ]
  alarm_name          = "${local.name_prefix}_shard_capacity_reached_90%"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 1
  evaluation_periods  = 1
  threshold           = 90

  metric_query {
    id          = "data_stream_raw"
    return_data = false
    metric {
      dimensions = {
        "StreamName" = aws_kinesis_stream.data.name
      }
      metric_name = "IncomingBytes"
      namespace   = "AWS/Kinesis"
      period      = 5 * 60
      stat        = "Sum"
    }
  }

  metric_query {
    id          = "data_stream"
    expression  = "FILL(data_stream_raw,0)"
    return_data = false
  }

  metric_query {
    expression  = "100*(data_stream_kb/data_stream_limit)"
    id          = "e_quotas"
    label       = "Quotas percentage"
    return_data = true
  }

  metric_query {
    expression  = "1000"
    id          = "kb_per_shard_limit"
    label       = "Kb quotas of single shard"
    return_data = false
  }

  metric_query {
    expression  = "${var.shard_count} * kb_per_shard_limit * PERIOD(data_stream) * IF(data_stream, 1, 1)"
    id          = "data_stream_limit"
    label       = "Incoming bytes Limit"
    return_data = false
  }

  metric_query {
    expression  = "data_stream/1000"
    id          = "data_stream_kb"
    label       = "Incoming kbytes"
    return_data = false
  }

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_metric_alarm"], {}),
    try(local.tags.named["aws_cloudwatch_metric_alarm"]["${local.name_prefix}_shard_capacity_reached_90%"], {})
  )
}
