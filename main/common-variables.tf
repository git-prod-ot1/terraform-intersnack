locals {
  env_prefix                 = terraform.workspace
  company_name_prefix        = "${local.env_prefix}_${var.company_namespace}"
  company_name_prefix_dashed = "${local.env_prefix}-${var.company_namespace}"
  tagging_configuration      = jsondecode(file("${path.root}/tagging_configuration.json"))

  typed_tags                 = try({
    for resource_type in local.tagging_configuration.defaults.resources_types : resource_type =>
    local.tagging_configuration.defaults.tags
  }, {})
  named_tags = {
    for resource_type, named_config in local.tagging_configuration : resource_type => try({
      for resource_name, tag_config in named_config : resource_name => tag_config.tags
    }, {})
    if resource_type != "defaults"
  }

  tags = {
    default : merge(var.tags.default, {
      namespace : var.company_namespace,
      environment : local.env_prefix
    }
    ),
    typed : local.typed_tags
    named : local.named_tags
  }
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
  type        = string
}

variable "region" {
  default     = "eu-central-1"
  description = "AWS Region"
  type        = string
}

