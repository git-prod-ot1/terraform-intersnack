resource "aws_cloudwatch_log_group" "firehose_video_index_delivery_stream" {
  name              = "/aws/kinesisfirehose/${local.name_prefix}_video_index_delivery_stream"
  retention_in_days = var.logs_retention_time
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["/aws/kinesisfirehose/${local.name_prefix}_video_index_delivery_stream"], {})
  )
}

resource "aws_cloudwatch_log_stream" "firehose_video_index_delivery_stream_s3" {
  name           = "${local.company_name_prefix}_S3Delivery"
  log_group_name = aws_cloudwatch_log_group.firehose_video_index_delivery_stream.name
}

resource "aws_cloudwatch_event_rule" "save_video_to_s3" {
  name                = "${local.name_prefix}_save_video_to_s3_rule"
  description         = "Save video to S3 periodically"
  schedule_expression = "cron(0/3 * * * ? *)"
  tags                = local.tags.default
}

resource "aws_cloudwatch_event_target" "lambda_video_to_s3" {
  rule = aws_cloudwatch_event_rule.save_video_to_s3.name
  arn  = module.dispatcher_lambda.aws_lambda_function.arn
}

resource "aws_lambda_permission" "lambda_v2_permissions" {
  action        = "lambda:InvokeFunction"
  function_name = module.dispatcher_lambda.aws_lambda_function.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.save_video_to_s3.arn
}

resource "aws_cloudwatch_metric_alarm" "stream_down" {
  count = var.video_stream_count

  alarm_name  = "${local.stream_base_name}_${format("%02d",count.index+1)}_Down"
  namespace   = "AWS/KinesisVideo"
  metric_name = "PutMedia.ActiveConnections"
  dimensions = {
    "StreamName" = "${local.stream_base_name}_${format("%02d",count.index+1)}"
  }
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = 3
  evaluation_periods  = 5
  period              = 2 * 60
  statistic           = "Maximum"
  threshold           = 1
  alarm_actions       = [
    var.aws_sns_topic_factory.arn
  ]
  treat_missing_data = "breaching"
  tags               = local.tags.default
}

resource "aws_cloudwatch_metric_alarm" "stream_name_down" {
  for_each = toset(var.required_streams)

  alarm_name  = "${local.name_prefix}_stream_down_(${local.stream_name_prefix}${each.value})"
  namespace   = "AWS/KinesisVideo"
  metric_name = "PutMedia.ActiveConnections"
  dimensions = {
    "StreamName" = "${local.stream_name_prefix}${each.value}"
  }
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = 3
  evaluation_periods  = 5
  period              = 2 * 60
  statistic           = "Maximum"
  threshold           = 1
  alarm_actions       = [
    var.aws_sns_topic_factory.arn
  ]
  treat_missing_data = "breaching"
  tags               = local.tags.default
}

resource "aws_cloudwatch_metric_alarm" "stream_low_mbps" {
  for_each = toset(var.required_streams)

  alarm_name  = "${local.name_prefix}_stream_low_mbps_(${local.stream_name_prefix}${each.value})"
  namespace   = "AWS/KinesisVideo"
  metric_name = "PutMedia.IncomingBytes"
  dimensions = {
    "StreamName" = "${local.stream_name_prefix}${each.value}"
  }
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = 3
  evaluation_periods  = 5
  period              = 2 * 60
  statistic           = "Average"
  threshold           = 2 * 1024 * 1024
  alarm_actions       = [
    var.aws_sns_topic_factory.arn
  ]
  treat_missing_data = "breaching"
  tags               = local.tags.default
}

resource "aws_cloudwatch_log_metric_filter" "lambda_error_metric_filter" {
  name           = "${module.dispatcher_lambda.aws_lambda_function.function_name}_error_log_metric_filter"
  pattern        = "%\\[ERROR\\]%"
  log_group_name = module.dispatcher_lambda.aws_cloudwatch_log_group.name

  metric_transformation {
    name      = "${module.dispatcher_lambda.aws_lambda_function.function_name}_error_count"
    namespace = "Lambda/Errors"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_error_alarm" {
  alarm_name          = "${local.name_prefix}_video_dispatcher_error"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  metric_name         = "${module.dispatcher_lambda.aws_lambda_function.function_name}_error_count"
  namespace           = "Lambda/Errors"
  period              = 900
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  alarm_description = "${title(var.unit_name)} Video Stream Data Archiver dispatcher failed to process"
  alarm_actions     = [var.sns_topic_arn]
  tags              = local.tags.default
  #  dimensions = {
  #    FunctionName = module.dispatcher_lambda.aws_lambda_function.function_name
  #  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_execution_alarm" {
  alarm_name          = "${module.dispatcher_lambda.aws_lambda_function.function_name}_execution"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = 3
  datapoints_to_alarm = 2
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = 900
  statistic           = "Sum"
  threshold           = 2
  treat_missing_data  = "notBreaching"
  alarm_description   = "${title(var.unit_name)} Video Stream Data Archiver dispatcher not triggered"
  alarm_actions       = [var.sns_topic_arn]
  tags                = local.tags.default
  dimensions = {
    FunctionName = module.dispatcher_lambda.aws_lambda_function.function_name
  }
}
