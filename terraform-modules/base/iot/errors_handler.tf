module "errors_handler" {
  source = "./errors_handler"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace

  iot_errors_sqs     = aws_sqs_queue.iot_errors
  iot_errors_sqs_dlq = aws_sqs_queue.dlq
  errors_bucket      = var.errors_bucket

  tags = local.tags
}
