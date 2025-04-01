variable "layer_name" {
  type = string
}

variable "source_files" {
  type = list(string)
}

variable "lib_location" {
  type = string
}

variable "aws_s3_bucket_lambda_layers" {}
