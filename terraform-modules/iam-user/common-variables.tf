locals {
  env_prefix                 = terraform.workspace
  unit_name                  = var.unit_name == null ? "" : var.unit_name
  unit_name_dashed           = replace(local.name_prefix, "_", "-")
  company_name_prefix        = "${local.env_prefix}_${var.company_namespace}"
  company_name_prefix_dashed = "${terraform.workspace}-${var.company_namespace}"
  name_prefix                = var.unit_name == null ? local.company_name_prefix : "${local.company_name_prefix}_${var.unit_name}"
  name_prefix_dashed         = replace(local.name_prefix, "_", "-")

  tags = merge(
    var.tags,
    {
      default : {
        for key, value in merge(var.tags[
        "default"
        ], {
          unit : local.unit_name
        }) : key => value if value != null && value != ""
      },
    })
}

variable "unit_name" {
  type        = string
  description = "Describes the common name of the unit. When omitted resource is created with company namespace only"
  default     = null
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
