variable "sqs" {
  type = object({
    arn = string,
    url = string
  })
}

variable "s3_data_bucket" {
  type = any
  description = "Reference to S3 data bucket"
}

variable "factory" {
  type        = string
  description = "Factory partition"
}
