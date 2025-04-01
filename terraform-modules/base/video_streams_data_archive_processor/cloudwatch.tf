resource "aws_cloudwatch_metric_alarm" "sqs_dlq_alarm" {
  alarm_name          = "${local.name_prefix}_video_sqs_processing"
  alarm_description   = "Video Stream Data Archiver failed to process"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 120
  statistic           = "Minimum"
  threshold           = 1
  actions_enabled     = true
  alarm_actions       = [var.sns_topic_arn]
  dimensions = {
    QueueName = aws_sqs_queue.videostreams_tasks_queue_dlq.name
  }
  treat_missing_data = "missing"
  tags               = local.tags.default
}
