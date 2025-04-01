resource "aws_sqs_queue" "videostreams_tasks_queue" {
  name                       = "${local.company_name_prefix_dashed}-videostreams"
  max_message_size           = 2048
  message_retention_seconds  = 172800
  delay_seconds              = 5
  visibility_timeout_seconds = var.videostreams_sqs_visibility_timeout_seconds

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.videostreams_tasks_queue_dlq.arn
    maxReceiveCount     = 5
  })

  sqs_managed_sse_enabled = true

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_sqs_queue"], {}),
    try(local.tags.named["aws_sqs_queue"]["${local.company_name_prefix_dashed}-videostreams"], {})
  )
}

resource "aws_sqs_queue" "videostreams_tasks_queue_dlq" {
  name                      = "${local.company_name_prefix_dashed}-videostreams-dlq"
  max_message_size          = 2048
  message_retention_seconds = 172800
  delay_seconds              = 5

  sqs_managed_sse_enabled = true

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_sqs_queue"], {}),
    try(local.tags.named["aws_sqs_queue"]["${local.company_name_prefix_dashed}-videostreams-dlq"], {})
  )
}

resource "aws_lambda_event_source_mapping" "queue_processor" {
  event_source_arn = aws_sqs_queue.videostreams_tasks_queue.arn
  function_name    = module.videostreams_processor.aws_lambda_function.function_name

  batch_size = 1
}
