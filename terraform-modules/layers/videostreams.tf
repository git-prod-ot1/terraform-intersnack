module "videostreams" {
  source = "./library"

  aws_s3_bucket_lambda_layers = module.lambda_layers.aws_s3_bucket
  layer_name = "videostreams"
  lib_location = "${path.module}/videostreams"
  source_files = [
    "${path.module}/videostreams/src/videostreams/videostreams.py"
  ]
}
