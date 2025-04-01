locals {
  capital_name      = title(var.unit_name)
  name_prefix_short = "${local.company_name_prefix}_${var.factory_short}"
}

variable "data_destinations" {
  type        = list(string)
  default     = ["ATHENA"]
  description = "List of data lake modules. \"ATHENA\" is a required module, \"TIMESTREAM\" can be added optionally"
  #  validation {
  #    condition = contains(var.data_destinations, "ATHENA")
  #    error_message = "ATHENA is currently required."
  #  }
  #  validation {
  #    condition = alltrue([
  #      for d in var.data_destinations : contains(["ATHENA", "TIMESTREAM"], d)
  #    ])
  #    error_message = "Allowed values for data_destinations are \"ATHENA\", or \"TIMESTREAM\"."
  #  }
}

variable "layers" {
  type        = any
  description = "Object holding info about globally accessible layers"
}

variable "transformation_lambda" {
  type        = any
  description = "Lambda resource used for transforming incoming data in Kinesis Firehose"
  default     = null
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

variable "measurement_samples_glue_table" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of dedicated glue table"
}

variable "factory_short" {
  type        = string
  description = "Short name of the factory, ex. gl for glinojeck"
}

variable "no_of_things" {
  type        = number
  default     = 1
  description = "Number of things to create"
}

variable "data_stream_shards" {
  type        = number
  default     = 1
  description = "Number of data shards for Kinesis"
}

variable "video_stream_count" {
  type        = number
  default     = 1
  description = "Number of Video streams. Used for creation of alarms"
}

variable "sns_alarms_recipients" {
  type        = list(string)
  default     = []
  description = "List of emails, that should be notified on events"
}

variable "glue_schema_extension_columns" {
  type = list(object({
    name = string,
    type = string
  }))
  default = []
}

variable "base" {
  type = object({
    measurement_samples_bucket                = any
    measurement_samples_glue_catalog_database = any
    aws_iam_lambda_role                       = any
    s3_video_feed_name                        = string
    aws_s3_bucket_s3_video_feed               = any
    pliot_arn                                 = any
    litmus_name                               = any
    aws_timestreamwrite_database              = any
  })
}

variable "enable_takenat_partitioning" {
  default     = true
  description = "If set to true, uses dynamic partitioning based on takenAt from transformation lambda. Takes precedence over dynamic_partitioning_prefix variable"
}

variable "dynamic_partitioning_prefix" {
  default     = null
  description = "If provided enables dynamic partitioning for Kinesis Firehose Stream"
}

variable "on_demand_mode" {
  default     = false
  description = "[experimental] If set to true, enables on_demand mode for kinesis stream instead of default PROVISIONED"
}

variable "timestream_table_names" {
  type        = list(string)
  description = "Timestream table names. Default table will be appended."
  default     = []
}

variable "timestream_magnetic_retention" {
  type        = number
  description = "Number of DAYS for magnetic store retention (semi-permanent access)"
  default     = 180
}

variable "timestream_memory_retention" {
  type        = number
  description = "Number of HOURS for memory store retention (fast-access)"
  default     = 2*24
}

variable "iot_error_actions_bucket" {
  type        = any
  description = "A reference to s3 bucket for error actions"
}

variable "timestream_table_skip_prefix" {
  type        = bool
  description = "If true, table namespace prefix is omitted (recommended) for timestream"
  default     = false
}

variable "timestream_table_prefix_override" {
  type        = string
  description = "If set overrides timestream default table prefix."
  default     = null
}

variable "timestream_default_table_name_override" {
  type        = string
  description = "If set overrides timestream default table name."
  default     = null
}

variable "monitoring_configuration" {
  description = "Configuration for monitoring submodule - additional iot2s3 for factory device monitoring purposes. Requires enabled monitoring in base."
  type        = object({
    no_of_things = number
    glue_table   = any
    s3_bucket    = any
    unit_name    = optional(string)
  })
  default = null
}

variable "enable_video_streams_data_dispatcher" {
  default     = false
  description = "Enable video streams data archiver. Requires video stream data archiver processor in base module."
}

variable "video_stream_aws_dynamodb_table" {
  default     = null
  description = "Video stream data archiver dynamodb table"
  type        = any
}

variable "video_streams_aws_sqs_queue" {
  default     = null
  description = "Video stream data archiver message queue"
  type        = any
}

variable "required_active_video_stream_names" {
  default     = []
  description = "Stream expected to be online. If no connection present it will produce alarm. Name preceded by standard name_prefix."
  type        = list(string)
}

variable "custom_video_prefix" {
  type        = string
  description = "Custom Video streams prefix"
  default     = null
}

variable "disable_no_data_alarm_for_client_number" {
  type        = list(number)
  description = "List of numbers of clients not expected to trigger no data cloud watch alarm"
  default     = []
}

variable "iot2s3_cloudwatch_alarms_config" {
  type    = any
  default = {
    datapoints_to_alarm : 1
    evaluation_periods : 1
    period : 15*60
  }
  description = "Configuration for iot2s3 cloudwatch alarm."
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}

variable "errors_bucket_name" {
  default = null
  type = string
  description = "Bucket name for storing not processable measurements"
}


variable "local_secrets" {
  type = bool
  default = false
  description = "If true, generates pem and key files locally"
}


variable "timestream" {
  type = object({
    partition_field = optional(string, "deviceName")
  })
}

variable "override_debug_client_creation" {
  type        = bool
  default     = false
  description = "If set to true overrides default workspace mechanism and creates the debug client"
}
