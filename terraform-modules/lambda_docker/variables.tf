variable "function_name_suffix" {
  type        = string
  description = "A suffix added to function name"
  default     = null
}

variable "permissions" {
  type = list(
    object({
      name   = string
      policy = any
    })
  )
  description = "A set of permissions to be included in assigned lambda role"
  default     = []
}

variable "permissions_managed" {
  type        = list(string)
  description = "A list of ARNs for managed policies"
  default     = []
}

variable "environment" {
  type    = map(string)
  default = {}
}

variable "timeout" {
  type        = number
  description = "Timeout in seconds"
  default     = 10
}

variable "memory_size" {
  type        = number
  description = "Lambda memory size"
  default     = 128
}

variable "iam_role" {
  type        = any
  description = "A reference to IAM Lambda Role"
  default     = null
}

variable "image_config" {
  type = object({
    working_directory = optional(string)
    command           = optional(list(string))
    entry_point       = optional(list(string))
  })
  default = null
}

variable "vpc_config" {
  type = object({
    security_group_ids = list(string)
    subnet_ids         = list(string)
  })
  default = null
}

variable "ephemeral_storage_size" {
  type = number
  default = 512
}

variable "reserved_concurrent_executions" {
  type = number
  default = -1
}