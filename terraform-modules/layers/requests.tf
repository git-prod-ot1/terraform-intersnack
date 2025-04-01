module "requests" {
  source = "./requirements-only"

  aws_s3_bucket_lambda_layers = module.lambda_layers.aws_s3_bucket
  layer_name = "requests"
  lib_location = "${path.module}/requests"
}
