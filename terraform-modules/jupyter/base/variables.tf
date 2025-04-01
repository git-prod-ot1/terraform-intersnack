variable "vpc" {
  type        = any
  description = "VPC definition object, required field: id"
}

variable "sns_topic_override" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of a dedicated topic inside the module"
}

variable "sns_alarms_recipients" {
  type        = list(string)
  default     = []
  description = "List of emails, that should be notified on events"
}

variable "sns_kms_arn" {
  type        = string
  description = "A KMS arn used to encrypt SNS for alarming"
}
