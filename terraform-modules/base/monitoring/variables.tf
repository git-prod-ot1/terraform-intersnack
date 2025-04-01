variable "measurement_samples_glue_catalog_database" {
  description = "Glue Catalog Database for measurement samples table"
}

variable "enable_takenat_partitioning" {
  description = "If set to true, uses dynamic partitioning based on takenAt from transformation lambda. Takes precedence over dynamic_partitioning_prefix variable"
}

variable "iot_error_actions_bucket" {
  description = "A reference to s3 bucket for error actions"
}

variable "glue_schema_extension_columns" {
  type = list(object({
    name = string,
    type = string
  }))
  default = []
}

variable "athena_table_name" {
  default = null
  type = string
  description = "Athena table name"
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}
