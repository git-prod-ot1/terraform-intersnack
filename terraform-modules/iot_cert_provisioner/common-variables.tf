locals {
  env_prefix                 = terraform.workspace
  unit_name_dashed           = replace(var.unit_name, "_", "-")
  company_name_prefix        = "${local.env_prefix}_${var.company_namespace}"
  company_name_prefix_dashed = "${terraform.workspace}-${var.company_namespace}"
  name_prefix                = "${local.company_name_prefix}_${var.unit_name}"
  name_prefix_dashed         = "${local.company_name_prefix_dashed}-${local.unit_name_dashed}"

  tags = merge(
    var.tags,
    {
      default : merge(var.tags["default"], {
        unit : var.unit_name
      }),
    }
  )
}

variable "unit_name" {
  type        = string
  description = "Describes the common name of the unit"
}

variable "company_namespace" {
  type        = string
  description = "Common prefix for company ex. plcf"
}

variable "tags" {
  description = "Tags"
  type        = any
}

variable "aws_user_id" {
  description = "AWS User id"
}

variable "region" {
  default     = "eu-central-1"
  description = "AWS Region"
}
