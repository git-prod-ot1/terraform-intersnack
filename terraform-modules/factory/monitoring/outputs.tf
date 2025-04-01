output "transformation_lambda" {
  value = module.iot2s3.transformation_lambda
}

output "data_topic" {
  value = module.iot2s3.aws_iot_data_topic
}
