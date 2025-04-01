locals {
  create_message_transform = var.transformation_lambda == null ? 1 : 0
  message_transform_lambda = coalesce(var.transformation_lambda, try(module.message_transform[0].function, null))
}

module "message_transform" {
  count  = local.create_message_transform
  source = "./message_transform"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name

  tags = local.tags

  glue_partitions_from_iot_rule_sql = var.glue_partitions_from_iot_rule_sql
  send_client_metrics               = var.send_client_metrics
  send_factory_metrics              = var.send_factory_metrics
}
