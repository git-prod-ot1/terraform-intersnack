variable "shard_count" {
  type        = number
  default     = 1
  description = "Number of shards required for Kinesis Streams. Should be calculated based on number and size of messages/s"
}

variable "on_demand_mode" {
  type        = bool
  default     = false
  description = "[experimental] If set to true, enables on_demand mode for kinesis stream instead of default PROVISIONED"
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS topic for alarming purposes"
}
