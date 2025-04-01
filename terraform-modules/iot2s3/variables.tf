variable "iot_certificate" {
  description = "Additional certificate to be applied to created policies"
  default     = null
}

variable "iot_policies" {
  description = "Additional policies to be applied to certificate"
  default     = []
}

variable "no_of_things" {
  type        = number
  default     = 1
  description = "Number of things to create"
}

variable "read_topics_below" {
  type        = bool
  default     = false
  description = "Adds /# at the end of IoT rule Topic filter"
}

variable "factory_partition_override" {
  type        = string
  description = "Override for prefix in S3, defaults to unit_name"
  default     = null
}

variable "sns_topic_override" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of a dedicated topic inside the module"
}

variable "sns_alarms_recipients" {
  type        = list(string)
  default     = []
  description = "List of emails, that should be notified on events"
}

variable "create_dashboard" {
  type        = bool
  default     = false
  description = "Controls whether a dashboard for a module should be created, is usually propagated from higher module"
}

variable "shard_count" {
  type        = number
  default     = 1
  description = "Number of shards required for Kinesis Streams. Should be calculated based on number and size of messages/s"
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

variable "measurement_samples_glue_table" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of dedicated glue table"
}

variable "measurement_samples_glue_catalog_database" {
  type        = any
  description = "Glue Catalog Database for measurement samples table"
}

variable "aws_iot_thing_type" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of dedicated thing type"
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

variable "glue_crawler_cron" {
  type        = string
  default     = null
  description = "Cron expression for scheduled Glue Crawler run. Defaults to cron(1 0 * * ? *). Default variable value not provided due to embedded modules behaviour (value is propagated from higher modules)"
}

variable "cloudwatch_alarms_evaluation_period" {
  type        = number
  default     = null
  description = "Overrides the default evaluation period of 900 seconds"
}

variable "cloudwatch_alarms_datapoints_to_alarm" {
  type        = number
  default     = 1
  description = "The number of datapoints that must be breaching to trigger the alarm."
}

variable "cloudwatch_alarms_evaluation_periods" {
  type        = number
  default     = 1
  description = "The number of periods over which data is compared to the specified threshold."
}

variable "on_demand_mode" {
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

variable "override_debug_client_creation" {
  type        = bool
  default     = false
  description = "If set to true overrides default workspace mechanism and creates the debug client"
}

variable "kinesis_partition_key" {
  default     = "$${newuuid()}"
  description = "A partition key used for IoT Rule sending to kinesis"
}

variable "iot_error_actions_bucket" {
  type        = any
  description = "A reference to s3 bucket for error actions"
}

variable "allow_wildcard_debug_client" {
  type        = bool
  default     = false
  description = "If set to true, allows wildcard debug client creation apart from the main debug client"
}

variable "glue_table_name_override" {
  type        = string
  default     = null
  description = "If provided, overrides name of created table name."
}

variable "bucket_name_override" {
  type        = string
  default     = null
  description = "If provided, overrides name of created s3 bucket."
}


variable "iot_rule_sql" {
  type        = string
  description = "If provided, overrides the SQL for default IoT rule"
  default     = null
}

variable "iot_rule_actions" {
  type = object({
    republish = list(object({
      role_arn = string
      topic    = string
      qos      = optional(number, 0)
    }))
  })
  default     = null
  description = "Configuration object for custom iot rules"
}

variable "topic" {
  type        = string
  description = "If provided overrides default data topic"
  default     = null
}

variable "disable_no_data_alarm_for_client_number" {
  type        = list(number)
  description = "List of numbers of clients not expected to trigger no data cloud watch alarm"
  default     = []
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}

variable "glue_partitions_from_iot_rule_sql" {
  type = string
  default = null
  description = "List of glue partitions expected in iot rule sql."
}

variable "default_iot_rule_enabled" {
  type = bool
  default = true
  description = "Enables/Disables the default IoT rule - used for overriding the behaviour of the IoT processing"
}

variable "aggregate_mode" {
  type = bool
  default = false
  description = "If true, skips creating of kinesis-stream (assuming it should be provided differently)"
}

variable "local_secrets" {
  type = bool
  default = false
  description = "If true, generates pem and key files locally"
}

variable "default_action_destination" {
  type        = string
  default     = "KINESIS"
  description = "Allowed values: KINESIS, FIREHOSE. Defines the iot default action destination."
  validation {
    condition = contains(["KINESIS", "FIREHOSE"],  var.default_action_destination)
    error_message = "Allowed values for default_action_destination are \"KINESIS\", or \"FIREHOSE\"."
  }
}

variable "send_client_metrics" {
  type        = bool
  default     = true
  description = "Flag to control process of sending client metrics"
}

variable "send_factory_metrics" {
  type        = bool
  default     = true
  description = "Flag to control process of sending factory metrics"
}

variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "If set to false, doesn't create the alarms for this module"
}
