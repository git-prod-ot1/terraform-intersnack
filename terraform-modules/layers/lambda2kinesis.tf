module "lambda2kinesis" {
  source = "./library"

  aws_s3_bucket_lambda_layers = module.lambda_layers.aws_s3_bucket
  layer_name = "lambda2kinesis"
  lib_location = "${path.module}/lambda2kinesis"
  source_files = [
    "${path.module}/lambda2kinesis/src/lambda2kinesis/lambda2kinesis.py"
  ]
}
