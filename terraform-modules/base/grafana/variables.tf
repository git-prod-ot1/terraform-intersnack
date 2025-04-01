variable "athena_output_bucket" {
  type        = any
  description = "Reference to S3 bucket for Athena Queries"
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
  default     = null
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
