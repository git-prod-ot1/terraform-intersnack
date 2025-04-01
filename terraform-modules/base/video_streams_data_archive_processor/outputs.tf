output "videostreams_sqs_visibility_timeout_seconds" {
  value = var.videostreams_sqs_visibility_timeout_seconds
}

output "lambda" {
  value = module.videostreams_processor.aws_lambda_function
}

output "aws_dynamodb_table" {
  value = aws_dynamodb_table.videostreams_tasks_table
}

output "aws_sqs_queue" {
  value = aws_sqs_queue.videostreams_tasks_queue
}
