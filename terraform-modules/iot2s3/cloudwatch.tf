resource "aws_cloudwatch_metric_alarm" "client_no_data" {
  count = var.enable_monitoring ? var.no_of_things : 0

  alarm_name         = "${aws_iot_thing.this[count.index].name}_no_data"
  treat_missing_data = "breaching"
  metric_query {
    id = "incoming_messages_client"
    metric {
      dimensions = {
        "ClientId" = aws_iot_thing.this[count.index].name
      }
      metric_name = "Messages.Incoming"
      namespace   = "IoTCoreCustom"
      period      = var.cloudwatch_alarms_evaluation_period == null ? 15 * 60 : var.cloudwatch_alarms_evaluation_period
      stat        = "Maximum"
    }
    return_data = true
  }
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = var.cloudwatch_alarms_datapoints_to_alarm
  evaluation_periods  = var.cloudwatch_alarms_evaluation_periods
  threshold           = 1
  alarm_actions = [
    local.sns_topic.arn
  ]
  actions_enabled = !contains(var.disable_no_data_alarm_for_client_number, (count.index+1))

  tags = local.tags.default
}
