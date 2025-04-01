output "aws_iot_thing" {
  value = aws_iot_thing.this
}

output "aws_iot_data_topic" {
  value = local.data_topic_name
}

output "aws_iot_certificate" {
  value = aws_iot_certificate.this
}

output "aws_iot_certificate_debug" {
  value = length(aws_iot_certificate.debug) > 0 ? aws_iot_certificate.debug[0] : null
}
