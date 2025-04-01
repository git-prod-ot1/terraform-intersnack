variable "function_name_suffix" {
  type        = string
  description = "A suffix added to function name"
  default     = null
}

variable "watch" {
  type        = list(string)
  description = "A list of file to watch"
  default     = []
}

variable "source_dir" {
  type        = string
  description = "A path to source directory"
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

variable "layers" {
  type        = list(string)
  description = "A list of layers arn"
  default     = []
}

variable "runtime" {
  type        = string
  description = "Runtime for lambda function"
  default     = "python3.9"
}

variable "handler" {
  type    = string
  default = "main.lambda_handler"
}

variable "vpc_config" {
  type = object({
    security_group_ids = list(string)
    subnet_ids         = list(string)
  })
  default = null
}

variable "reserved_concurrent_executions" {
  type = number
  default = -1
}
