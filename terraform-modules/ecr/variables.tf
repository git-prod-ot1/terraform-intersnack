variable "alpha_version_count" {
  description = "Number of '-alpha' images to keep"
  type        = number
  default     = 5
}

variable "release_version_count" {
  description = "Number of '-release' images to keep"
  type        = number
  default     = 5
}

variable "default_retention_days" {
  description = "Retention period in days for images neither '-alpha' nor '-release'"
  type        = number
  default     = 30
}

variable "ignore_name_prefix" {
  description = "If true, uses unit name instead of name_prefix"
  type        = bool
  default     = false
}