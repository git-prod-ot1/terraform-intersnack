variable "iot_errors_sqs" {
  type = any
  description = "A reference to the iot errors SQS"
}

variable "iot_errors_sqs_dlq" {
  type = any
  description = "A reference to the iot errors SQS DLQ"
}


variable "errors_bucket" {
  type = any
  description = "A reference to the S3 bucket where the final errors should be stored"
}
