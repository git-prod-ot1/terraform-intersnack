module "monitoring" {
  count  = var.enable_monitoring == true ? 1 : 0
  source = "./monitoring"

  unit_name         = "monitoring"
  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  enable_takenat_partitioning               = true
  measurement_samples_glue_catalog_database = aws_glue_catalog_database.measurement_samples_database
  iot_error_actions_bucket                  = module.iot_rules_actions_logs.aws_s3_bucket
  athena_table_name                         = var.monitoring_athena_table_name
  partitioning_lambda_version               = var.partitioning_lambda_version
  glue_schema_extension_columns             = [
    {
      name = "additionaldata"
      type = "string"
    },
    {
      name = "devicename"
      type = "string"
    }
  ]
}
