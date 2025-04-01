variable "ecs_cluster_arn" {
  type        = string
  description = "An ARN of the ECS cluster that should be monitored for stopped tasks"
}

variable "sns_topic_arn" {
  type        = string
  description = "The ARN of the SNS topic that should be notified of failed tasks"
}

variable "cloudwatch_log_group" {
  type        = any
  description = "A reference to cloudwatch log group"
}

variable "sns_kms_arn" {
  type        = string
  description = "A KMS arn used to encrypt SNS for alarming"
}
