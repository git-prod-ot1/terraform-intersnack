locals {
  env_prefix                 = terraform.workspace
  company_name_prefix        = "${local.env_prefix}_${var.company_namespace}"
  company_name_prefix_dashed = "${terraform.workspace}-${var.company_namespace}"
  name_prefix                = local.company_name_prefix
  name_prefix_dashed         = local.company_name_prefix_dashed

  tags = {
    default : merge(var.tags["default"], {
      company : var.company_namespace
    }
    )
  }
}

variable "company_namespace" {
  type = string
}

variable "tags" {
  description = "Tags"
  type        = any
}

variable "aws_user_id" {
  description = "AWS User id"
}

variable "region" {
  default = "eu-central-1"
}

variable "role_arn" {
  type = string
}
