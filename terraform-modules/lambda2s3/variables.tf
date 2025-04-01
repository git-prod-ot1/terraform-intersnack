locals {
  index_bucket = var.index_bucket == null ? module.index[0].aws_s3_bucket : var.index_bucket
}

variable "factory_partition_override" {
  type        = string
  description = "Override for prefix in S3, defaults to unit_name"
  default     = null
}

variable "input_lambda" {
  type        = any
  description = "Lambda resource for providing incoming data"
}

variable "schedule_expression" {
  type        = string
  description = "Lambda resource cron schedule expression"
}

variable "transformation_lambda" {
  type        = any
  description = "Lambda resource used for transforming incoming data in Kinesis Firehose"
  default     = null
}

variable "index_bucket" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of dedicated bucket for index"
}

variable "measurement_samples_bucket" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of dedicated bucket for measurement samples"
}

variable "measurement_samples_glue_catalog_database" {
  type        = any
  description = "Glue Catalog Database for measurement samples table"
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
  default     = []
  description = "List of columns for Glue table that extend glue_schema_columns"
}

variable "firehose_source" {
  type        = string
  default     = "KINESIS"
  description = "Allowed values: KINESIS, DIRECT_PUT. Defines the firehose source configuration. For KINESIS: kinesis_source_configuration, for DIRECT_PUT: no source configuration block."
  validation {
    condition = contains(["KINESIS", "DIRECT_PUT"], var.firehose_source)
    error_message = "Allowed values for firehose_source are \"KINESIS\", or \"DIRECT_PUT\"."
  }
}

variable "on_demand_mode" {
  type        = bool
  default     = false
  description = "[experimental] If set to true, enables on_demand mode for kinesis stream instead of default PROVISIONED"
}

variable "enable_takenat_partitioning" {
  default     = false
  description = "[experimental] If set to true, uses dynamic partitioning based on takenAt from transformation lambda. Takes precedence over dynamic_partitioning_prefix variable"
}

variable "dynamic_partitioning_prefix" {
  default     = null
  description = "[experimental] If provided enables dynamic partitioning for Kinesis Firehose Stream"
}

variable "glue_partitions_updater" {
  type        = string
  default     = "GLUE_CRAWLER"
  description = "Allowed values: GLUE_CRAWLER,LAMBDA. For GLUE_CRAWLER: cron for generated crawler is set, for LAMBDA, lambda that runs each hour is created"
  validation {
    condition     = contains(["GLUE_CRAWLER", "LAMBDA"], var.glue_partitions_updater)
    error_message = "Allowed values for glue_partitions_updater are \"GLUE_CRAWLER\", or \"LAMBDA\"."
  }
}

variable "is_enabled" {
  type        = bool
  default     = true
  description = "Allows to disable a cloudwatch event triggering lambda"
}

variable "custom_s3_location" {
  type        = string
  default     = null
  description = "If provided, overrides default s3_location"
}

variable "glue_partition_keys" {
  type        = any
  description = "A list of partition keys"
  default     = null
}

variable "sns_alarms_recipients" {
  type        = list(string)
  default     = []
  description = "List of emails, that should be notified on events"
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}
