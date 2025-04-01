variable "bucket_name" {
  type        = string
  description = "Bucket name after prefix"
}

variable "use_ssl" {
  type        = bool
  default     = true
  description = "Enables encryption in transit"
}

variable "enable_encryption_at_rest" {
  type        = bool
  default     = true
  description = "Enables encryption at rest"
}

variable "block_public_access" {
  type        = bool
  default     = true
  description = "Blocks all public access"
}

variable "enable_versioning" {
  type        = bool
  default     = false
  description = "Enables versioning for all objects in a bucket"
}

variable "bucket_name_override" {
  type        = string
  description = "Override for s3 bucket name"
  default     = null
}

variable "bucket_policy_statements" {
  type        = any
  description = "A list of statements that should be attached to S3 policy. Type is not a list to not enforce a single format"
  default     = []
}

variable "bucket_lifecycle_configuration" {
  type = list(object({
    storage_class   = string
    transition_time_days = string
  }))
  description = "A list of lifecycle rules with storage class and transition time."
  default = []
}
