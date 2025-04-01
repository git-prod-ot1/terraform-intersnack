variable "workspace_url" {
  type        = string
  description = "Url of Grafana workspace"
}

variable "auth" {
  type        = string
  description = "Grafana Auth (most likely API Key)"
}

variable "athena_database" {
  type        = any
  description = "Reference to athena (glue) database"
}

variable "athena_output_s3_bucket" {
  type        = any
  description = "Reference to s3 bucket for Athena queries results"
}

variable "timestream_table" {
  type        = any
  default = null
  description = "Reference to timestream table"
}
