output "measurement_samples_bucket" {
  value = local.measurement_samples_bucket
}

output "kinesis_data_stream" {
  value = try(module.kinesis_stream[0].kinesis_data_stream,null)
}

output "firehose_stream" {
  value = aws_kinesis_firehose_delivery_stream.data
}

output "aws_iam_role_firehose" {
  value = aws_iam_role.firehose
}

output "dashboard_body" {
  value = local.dashboard_body
}

output "glue_table_name" {
  value = local.measurement_samples_glue_table.name
}

output "measurement_samples_glue_table" {
  value = local.measurement_samples_glue_table
}

output "transformation_lambda" {
  value = local.message_transform_lambda
}
