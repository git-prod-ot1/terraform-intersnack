variable "subnets" {
  type = object({
    private = list(object({ id = string, availability_zone = string }))
    public  = list(object({ id = string, availability_zone = string }))
  })
}

variable "vpc" {
  type        = any
  description = "Reference to VPC resource"
}

variable "allow_ingress_from_security_groups" {
  description = "Provided security groups (inside vpc) will be allowed to connect on database port."
  default     = []
}

variable "rds_backups_s3_buckets" {
  description = "Optional: S3 Buckets for backup/restore."
  default     = []
  type        = list(string)
}

variable "db_instance_name" {
  description = "Rename db instance"
  default     = null
}

variable "ingress_allow_all" {
  description = "Create rules to allow cidr 0.0.0.0/0"
  default = true
}
