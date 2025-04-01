locals {
  default_table_name = lower("${var.unit_name}_measurement_samplesdata")
}

module "glue" {
  source = "../../../terraform-modules/glue/table"

  aws_user_id                    = var.aws_user_id
  company_namespace              = var.company_namespace
  s3_location                    = "s3://${module.measurement_samples.aws_s3_bucket.bucket}/data/"
  table_name                     = var.athena_table_name == null ? local.default_table_name : var.athena_table_name
  tags                           = var.tags
  aws_glue_catalog_database_name = var.measurement_samples_glue_catalog_database.name
  glue_schema_extension_columns  = var.glue_schema_extension_columns
  partitioning_lambda_version    = var.partitioning_lambda_version
}
