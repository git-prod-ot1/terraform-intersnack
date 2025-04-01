variable "videostreams_sqs_visibility_timeout_seconds" {
  type = number
  default = 20
}

variable "layers" {
  type        = any
  description = "Object representing layers from layers module output"
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS topic for alarming purposes"
}
