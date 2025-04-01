locals {
  default_monitoring_unit_name = "${var.unit_name}monitoring"
}

module "monitoring" {
  count = var.monitoring_configuration == null ? 0 : 1
  source = "./monitoring"

  unit_name         = var.monitoring_configuration.unit_name == null ? local.default_monitoring_unit_name : var.monitoring_configuration.unit_name
  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  no_of_things                              = var.monitoring_configuration.no_of_things
  measurement_samples_glue_catalog_database = var.measurement_samples_glue_catalog_database
  measurement_samples_glue_table            = var.monitoring_configuration.glue_table
  measurement_samples_bucket                = var.monitoring_configuration.s3_bucket
  iot_error_actions_bucket                  = var.iot_error_actions_bucket
}
