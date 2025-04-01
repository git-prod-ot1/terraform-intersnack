variable "kinesis_data_stream" {
  description = "Kinesis stream for republish lambda."
}

variable "republish_topic" {
  description = "IoT republish topic name"
  type        = string
}

variable "reference_table_bucket" {
  description = "S3 bucket with reference table named <unit_name>.json"
  type        = string
}

variable "layers" {
  description = "Object holding info about globally accessible layers"
  type        = any
}

variable "republisher_store" {
  type = object({
    factory_short: string
    data_stream_shards : number
    measurement_samples_glue_catalog_database : any
    measurement_samples_bucket : any
    measurement_samples_glue_table : any
    sns_alarms_recipients : any
    error_bucket : any
  })
  default = null
  description = "Data related to republisher store. Should be set only if there is a need of storing republished data."
}