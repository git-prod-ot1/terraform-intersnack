variable "sqs" {
  type = object({
    arn = string,
    url = string
  })
}

variable "target_timestream" {
  type = object({
    database = string,
    table = string,
  })
}


variable "s3_data_bucket" {
  type = any
  description = "Reference to S3 data bucket"
}
