output "kinesis_widgets" {
  value = local.kinesis_widgets
  description = "Definition of Kinesis Stream related widgets to be added to metrics dashboard"
}

output "kinesis_data_stream" {
  value = aws_kinesis_stream.data
  description = "A reference to created AWS Kinesis data stream"
}
