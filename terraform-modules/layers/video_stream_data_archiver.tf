module "video_stream_data_archiver" {
  source = "./library"

  aws_s3_bucket_lambda_layers = module.lambda_layers.aws_s3_bucket
  layer_name = "video_stream_data_archiver"
  lib_location = "${path.module}/video_stream_data_archiver"
  source_files = [
    "${path.module}/video_stream_data_archiver/src/video_stream_data_archiver/video_stream_data_archiver.py"
  ]
}
