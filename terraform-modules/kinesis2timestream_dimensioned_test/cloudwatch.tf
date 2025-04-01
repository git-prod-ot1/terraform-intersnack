resource "aws_cloudwatch_metric_alarm" "iterator_age" {
  alarm_name          = "${local.name_prefix}_iterator_age"
  alarm_description   = "Iterator age is older than 30s. Lambda is failing to process kinesis messages"
  treat_missing_data  = "missing"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 3
  threshold           = 30 * 1000
  metric_name         = "IteratorAge"
  namespace           = "AWS/Lambda"
  dimensions          = {
    "FunctionName" = module.kinesis2timestream.aws_lambda_function.function_name
  }
  period    = 60
  statistic = "Maximum"


  alarm_actions = [
    var.alarm_sns_topic.arn
  ]

  tags = local.tags.default
}

resource "aws_cloudwatch_metric_alarm" "error" {
  alarm_name          = "${local.name_prefix}_error"
  alarm_description   = "Processing lambda encountered errors. Requires attention"
  treat_missing_data  = "missing"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 0
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  dimensions          = {
    "FunctionName" = module.kinesis2timestream.aws_lambda_function.function_name
  }
  period    = 60
  statistic = "Sum"


  alarm_actions = [
    var.alarm_sns_topic.arn
  ]

  tags = local.tags.default
}

