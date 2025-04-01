locals {
  capital_name       = title(var.unit_name)
  name_prefix_short  = "${local.company_name_prefix}_${var.factory_short}"
  stream_base_name   = "${local.company_name_prefix}_${upper(var.factory_short)}_Stream"
  stream_name_prefix = "${local.company_name_prefix}_${var.factory_short}_"
}

variable "aws_iam_role_firehose" {
  type        = any
  description = "Reference to IAM role for firehose"
}

variable "aws_s3_bucket_measurement_samples" {
  type        = any
  description = "Reference to measurement samples bucket resource"
}

variable "video_stream_count" {
  type        = number
  default     = 0
  description = "Number of Video streams. Used for creation of alarms"
}

variable "factory_short" {
  type        = string
  description = "Short name of the factory, ex. gl for glinojeck"
}

variable "aws_sns_topic_factory" {
  type        = any
  description = "Reference to SNS topic for alarms"
}

variable "aws_iam_lambda_role" {
  type        = any
  description = "Reference to default IAM role for lambda"
}

variable "layers" {
  type        = any
  description = "Object holding info about globally accessible layers"
}

variable "measurement_samples_glue_catalog_database" {
  type        = any
  description = "Glue Catalog Database for measurement samples table"
}

variable "base_widgets_length" {
  type        = number
  description = "Dashboard widget length"
}

variable "last_widgets_y_pos" {
  type        = number
  description = "Value calculated based on existing widgets in factory dashboard"
}

variable "widget_height" {
  type        = number
  description = "Default height of widget in dashboard"
}

variable "aws_s3_bucket_s3_video_feed" {
  type        = any
  description = "S3 bucket for video feed"
}

variable "logs_retention_time" {
  default = 7
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS topic for alarming purposes"
}

variable "aws_dynamodb_table" {
  default     = null
  description = "Video stream data archiver dynamodb table"
  type        = any
}

variable "aws_sqs_queue" {
  default     = null
  description = "Video stream data archiver message queue"
  type        = any
}

variable "required_streams" {
  default     = []
  type        = list(string)
  description = "Stream expected to be on. If no connection present it will produce alarm. Name preceded by standard name_prefix."
}

variable "custom_video_prefix" {
  type        = string
  description = "Custom Video streams prefix"
  default     = null
}
