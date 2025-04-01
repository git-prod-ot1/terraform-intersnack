variable "layers" {
  type        = any
  description = "Object representing layers from layers module output"
}

variable "grafana_enabled" {
  type        = bool
  description = "If enabled, dedicated grafana workspace is created"
  default     = false
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

variable "sns_topic" {
  type        = any
  default     = null
  description = "If provided, overrides the creation of a dedicated topic inside the module"
}

variable "sns_alarms_recipients" {
  type        = list(string)
  default     = []
  description = "List of emails, that should be notified on events"
}

variable "subnets" {
  type = object({
    private = list(object({ id = string }))
    public  = list(object({ id = string }))
  })
  default = null
}

variable "vpc" {
  type        = any
  description = "Reference to VPC resource"
  default = null
}

variable "enable_monitoring" {
  description = "Base for additional factory module for devices monitoring."
  type        = bool
  default     = false
}

variable "enable_video_streams_data_processor" {
  default     = false
  type        = bool
  description = "Enable video streams data archiver. Required by factory dispatcher."
}

variable "enable_grafana_networking" {
  default     = false
  type        = bool
  description = "Enable grafana networking, if provided, configures additional grafana settings allowing connection to VPC, for example to RDS dbs"
}

variable "grafana_extra_policies_arns" {
  type        = list(string)
  default     = []
  description = "List of extra policies to attach to grafana role"
}

variable "grafana_extra_data_sources" {
  type        = list(string)
  default     = []
  description = "List of extra data sources to attach to grafana role"
}

variable "query_output_bucket_name" {
  default     = null
  type        = string
  description = "Name of athena queries s3 output bucket"
}

variable "picture_feed_s3_lifecycle_configuration" {
  type = list(object({
    storage_class        = string
    transition_time_days = string
  }))
  description = "If provided, defines a list of lifecycle rules for picture-feed bucket."
  default = []
}

variable "video_feed_s3_lifecycle_configuration" {
  type = list(object({
    storage_class        = string
    transition_time_days = string
  }))
  description = "If provided, defines a list of lifecycle rules for video-feed bucket."
  default = []
}

variable "monitoring_athena_table_name" {
  default = null
  type = string
  description = "Name of athena table for factory monitoring"
}

variable "partitioning_lambda_version" {
  type    = number
  default = 2
  validation {
    error_message = "Supported versions: 1, 2."
    condition     = var.partitioning_lambda_version == 1 || var.partitioning_lambda_version == 2
  }
}
