resource "aws_sqs_queue" "iot_errors" {
  name                       = "${local.name_prefix}_iot_rules_errors"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 345600 # 4 days
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 70  # Slightly more than 1 minute to account for Lambda execution time

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })

  tags = local.tags.default
}

resource "aws_sqs_queue_policy" "iot_errors" {
  policy    = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sqs.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.dlq.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sqs_queue.iot_errors.arn
          }
        }
      }
    ]
  })
  queue_url = aws_sqs_queue.iot_errors.url
}

resource "aws_sqs_queue" "dlq" {
  name = "${local.name_prefix}_iot_rules_errors_dlq"
  tags = local.tags.default
}
