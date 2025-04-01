locals {
  glue_schema_columns = concat(var.glue_schema_columns, var.glue_schema_extension_columns)
}

variable "aws_glue_catalog_database_name" {
  type        = string
  description = "A name of a glue database where the table should be created"
}


variable "table_name" {
  type        = string
  description = "A name of a table without a prefix"
}

variable "partition_keys" {
  type        = any
  description = "A list of partition keys"
  default     = null
}

variable "s3_location" {
  type        = string
  description = "A location where the data is stored in s3 ex. s3://some_data_bucket/data/"
}

variable "glue_schema_columns" {
  type = list(object({
    name = string,
    type = string
  }))
  default = [
    {
      name = "datapointid"
      type = "string"
    },
    {
      name = "value"
      type = "string"
    },
    {
      name = "takenat"
      type = "timestamp"
    },
    {
      name = "takenatend"
      type = "timestamp"
    },
    {
      name = "postedat"
      type = "timestamp"
    },
    {
      name = "receivedat"
      type = "timestamp"
    },
    {
      name = "hour"
      type = "string"
    },
    {
      name = "invocationid"
      type = "string"
    }
  ]
  description = "Configuration of default columns for Glue table"
}

variable "glue_schema_extension_columns" {
  type = list(object({
    name = string,
    type = string
  }))
  default = []
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}
