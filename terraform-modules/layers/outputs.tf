output "layers" {
  value = {
    "lambda2kinesis" : module.lambda2kinesis.aws_lambda_layer_version,
    "videostreams" : module.videostreams.aws_lambda_layer_version,
    "requests" : module.requests.aws_lambda_layer_version,
    "pytz" : module.pytz.aws_lambda_layer_version,
    "mqtt" : module.mqtt.aws_lambda_layer_version,
    "video_stream_data_archiver" : module.video_stream_data_archiver.aws_lambda_layer_version,
  }
}

output "aws_s3_bucket_lambda_layers" {
  value = module.lambda_layers.aws_s3_bucket
}
