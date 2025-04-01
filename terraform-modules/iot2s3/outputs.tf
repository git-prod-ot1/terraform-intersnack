output "aws_iam_role_firehose" {
  value = module.kinesis2s3.aws_iam_role_firehose
}

output "measurement_samples_bucket" {
  value = module.kinesis2s3.measurement_samples_bucket
}

output "dashboard_body" {
  value = local.dashboard_body
}

output "aws_iot_thing" {
  value = local.iot_type
}

output "aws_iot_topic_rule" {
  value = aws_iot_topic_rule.this
}

output "aws_iot_data_topic" {
  value = local.data_topic_name
}

output "rule_topic" {
  value = local.rule_topic
}

output "aws_iot_certificate" {
  value = aws_iot_certificate.this
}

output "aws_iot_certificate_debug" {
  value = length(aws_iot_certificate.debug) > 0 ? aws_iot_certificate.debug[0] : null
}

output "kinesis_data_stream" {
  value = module.kinesis2s3.kinesis_data_stream
}

output "firehose_stream" {
  value = module.kinesis2s3.firehose_stream
}

output "alarms_sns_topic" {
  value = local.sns_topic
}

output "glue_table_name" {
  value = module.kinesis2s3.glue_table_name
}

output "measurement_samples_glue_table" {
  value = module.kinesis2s3.measurement_samples_glue_table
}

output "transformation_lambda" {
  value = module.kinesis2s3.transformation_lambda
}

output "iot_errors_iam_role" {
  value = aws_iam_role.iot_error_actions
  description = "A role used for storing errors in S3 during IoT roles processing"
}

output "iot_iam_role" {
  value = aws_iam_role.iot_role
  description = "A role used in IoT for rule execution, mostly with Kinesis permissions, only here for a temporary use"
}

output "error_queue_url" {
  value = data.aws_sqs_queue.iot_errors.url
}
