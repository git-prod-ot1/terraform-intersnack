output "lambda" {
  value = module.dispatcher_lambda.aws_lambda_function
}

output "dashboard_widgets" {
  value = local.widgets
}

output "kinesis_stream_active_connections_overview" {
  value = local.kinesis_stream_active_connections_overview
}

output "kinesis_video_streams_bitrate_metric" {
  value = local.kinesis_video_streams_bitrate_metric
}
