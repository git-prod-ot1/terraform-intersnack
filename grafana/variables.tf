locals {
  tags = {
    default : merge(var.tags.default, {
      company : var.company_namespace,
      environment : terraform.workspace
    }
    )
  }
  env_prefix  = terraform.workspace
  name_prefix = "${local.env_prefix}_${var.company_namespace}"
}

variable "region" {
  description = "AWS Region Name"
  default     = "eu-central-1"
}

variable "tags" {
  description = "Tags"
  type        = any
}

variable "aws_user_id" {
  description = "AWS User id"
}

variable "company_namespace" {
  description = "Common prefix for company ex. plcf"
}

variable "grafana_auth" {
  description = "Grafana api key"
  type        = string
}

variable "role_arn" {
  type = string
}
