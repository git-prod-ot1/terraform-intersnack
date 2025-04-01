locals {
  env_prefix                 = terraform.workspace
  unit_name_dashed = replace(var.unit_name, "_", "-")
  company_name_prefix        = "${local.env_prefix}_${var.company_namespace}"
  company_name_prefix_dashed = "${terraform.workspace}-${var.company_namespace}"
  name_prefix                = local.company_name_prefix
  name_prefix_dashed         = local.company_name_prefix_dashed

  non_null_maintenance_tags = {
    for k, v in var.maintenance_tags : k => v if v != null && v != ""
  }

  tags = merge(
    var.tags,
    {
      default : merge(
        local.non_null_maintenance_tags,
        var.tags["default"],
        {
          unit : var.unit_name
        },
      ),
    })
}

variable "unit_name" {
  type        = string
  description = "Describes the common name of the unit"
  default = "base"
}

variable "company_namespace" {
  type        = string
  description = "Common prefix for company ex. plcf"
}

variable "maintenance_tags" {
  description = "A set of tags required by guidelines, check https://pfeifer-langen.atlassian.net/wiki/spaces/AG/pages/3054109366/Tagging+Guidelines for details"

  nullable = false
  type = object({
    Company        = string
    Department = optional(string)
    Factory        = string
    CostCenter = optional(string)
    Product = optional(string)
    Project = optional(string)
    Process = optional(string)
    ProductOwner = string
    TechnicalOwner = string
    CreatedBy      = string
  })
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
  type        = string
}

