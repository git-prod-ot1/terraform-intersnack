variable "glue_partitions_from_iot_rule_sql" {
  type = string
  default = null
  description = "List of glue partitions expected in iot rule sql."
}

variable "send_client_metrics" {
  type = bool
  default = true
  description = "Flag to control process of sending client metrics"
}

variable "send_factory_metrics" {
  type = bool
  default = true
  description = "Flag to control process of sending factory metrics"
}
