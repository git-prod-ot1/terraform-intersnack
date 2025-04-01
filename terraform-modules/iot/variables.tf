variable "no_of_things" {
  type        = number
  default     = 1
  description = "Number of things to create"
}

variable "aws_iot_thing_type" {
  type        = number
  default     = null
  description = "If provided, overrides the creation of dedicated thing type"
}

variable "permissions_iot_policy" {
  default     = null
  description = "If provided, overrides the creation of default permissions policy for clients"
}

variable "override_debug_client_creation" {
  type        = bool
  default     = false
  description = "If set to true overrides default workspace mechanism and creates the debug client"
}

variable "iot_policies" {
  description = "Additional policies to be applied to certificate"
  default     = []
}

variable "topic" {
  type        = string
  description = "If provided overrides default data topic"
  default     = null
}

variable "allow_wildcard_debug_client" {
  type        = bool
  default     = false
  description = "If set to true, allows wildcard debug client creation apart from the main debug client"
}

