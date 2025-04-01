variable "republished_data_topic" {
  description = "Name of topic where data are republished"
  type        = string
}

variable "data_stream_shards" {
  type        = number
  default     = 1
  description = "Number of data shards for republished data's Kinesis"
}

variable "measurement_samples_glue_catalog_database" {
  type        = any
  description = "A name of a glue database where the table should be created"
}

variable "measurement_samples_bucket" {
  type        = any
  description = "Overrides the creation of dedicated bucket for measurement samples"
}

variable "measurement_samples_glue_table" {
  type        = any
  description = "If provided, overrides the creation of dedicated glue table"
}

variable "sns_alarms_recipients" {
  type = list(string)
  description = "List of emails, that should be notified on events"
}

variable "error_bucket" {
  type        = any
  description = "Dedicated bucket for errors for republisher_store"
}

variable "factory_name" {
  type = string
  description = "Name of the factory that republish data"
}