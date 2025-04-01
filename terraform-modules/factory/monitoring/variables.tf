variable "measurement_samples_glue_catalog_database" {
  description = "Glue Catalog Database for measurement samples table"
}

variable "no_of_things" {
  description = "Number of things to create"
  type        = number
  default     = 1
}

variable "iot_error_actions_bucket" {
  description = "A reference to s3 bucket for error actions"
}

variable "measurement_samples_glue_table" {
  description = "If provided, overrides the creation of dedicated glue table"
}

variable "measurement_samples_bucket" {
  description = "If provided, overrides the creation of dedicated bucket for measurement samples"
}

