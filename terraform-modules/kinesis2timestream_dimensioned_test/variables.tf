variable "kinesis_stream" {
  type        = any
  description = "Kinesis stream resource to consume data from"
}

variable "timestream_db" {
  type        = any
  description = "If provided, overrides creation of timestream db"
  default     = null
}

variable "timestream_db_name" {
  type        = any
  description = "If provided, overrides creation of timestream db"
  default     = null
}

variable "timestream_table_names" {
  type        = list(string)
  description = "Timestream table names. Default table will be appended."
  default     = []
}

variable "lambda_trigger_batch_size" {
  type        = number
  description = "Configures maximum of records that should be consumed from kinesis stream by lambda"
  default     = 25
}

variable "lambda_trigger_batch_window" {
  type        = number
  description = "Configures maximum time window lambda trigger should wait for records until proceeding"
  default     = 0
}

variable "timestream_dimension" {
  type        = string
  description = "Default dimension for timestream records, recommended value: factory name"
}

variable "timestream_magnetic_retention" {
  type        = number
  description = "Number of DAYS for magnetic store retention (semi-permanent access)"
  default     = 7
}

variable "timestream_memory_retention" {
  type        = number
  description = "Number of HOURS for memory store retention (fast-access)"
  default     = 2*24
}

variable "timestream_write_batch_size" {
  type        = number
  description = "Number of records to be saved in one API call to timestream (max. 100)"
  default     = 100
}

variable "alarm_sns_topic" {
  type        = any
  description = "Reference to SNS topic resource"
}

variable "table_skip_prefix" {
  type        = bool
  description = "If true, table namespace prefix is omitted (recommended)"
  default     = false
}

variable "table_prefix_override" {
  type        = string
  description = "If set overrides default table prefix."
  default     = null
}

variable "table_suffix" {
  type = string
  description = "Suffix to append to each table name, used in dynamic partitioning"
  default = null
}

variable "timestream_partition_field" {
  type = string
  description = "Field used for partitioning tables"
  default = "deviceName" // that should be refactored in the future
}

variable "default_table_name_override" {
  type        = string
  description = "If set overrides default table name (ignores prefix param)."
  default     = null
}

variable "errors_bucket_name" {
  default = null
  type = string
  description = "Bucket name for storing not processable measurements"
}

variable "infer_types" {
  default = false
  type = bool
  description = "If true, tries to infer type from value"
}
