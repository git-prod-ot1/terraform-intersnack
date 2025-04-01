variable "layer_name" {
  type = string
}

variable "lib_location" {
  type = string
}

variable "aws_s3_bucket_lambda_layers" {}

variable "build_script" {
  default = null
}
