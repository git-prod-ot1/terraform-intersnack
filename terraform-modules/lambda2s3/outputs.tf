output "aws_iam_role_input_lambda" {
  value = aws_iam_role.input_lambda
}

output "aws_kinesis_stream_data" {
  value = module.kinesis2s3.kinesis_data_stream
}

output "firehose_stream" {
  value = module.kinesis2s3.firehose_stream
}

output "aws_s3_bucket_index" {
  value = length(module.index) > 0 ? module.index[0].aws_s3_bucket : null
}

output "transformation_lambda" {
  value = module.kinesis2s3.transformation_lambda
}
