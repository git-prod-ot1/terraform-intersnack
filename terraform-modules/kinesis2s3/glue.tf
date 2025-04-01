locals {
  create_glue_table              = var.measurement_samples_glue_table == null ? 1 : 0
  // this is one hacky solution. For details, please reference this: https://github.com/hashicorp/terraform/issues/22405#issuecomment-625619906
  measurement_samples_glue_table = var.measurement_samples_glue_table == null ? module.measurement_samplesdata_glue_table[0].table : var.measurement_samples_glue_table
  table_name                     = var.glue_table_name_override == null ? lower("${var.unit_name}_measurement_samplesdata") : var.glue_table_name_override
  s3_location                    = coalesce(var.custom_s3_location, "s3://${local.measurement_samples_bucket.bucket}/data/")
}

module "measurement_samplesdata_glue_table" {
  count  = local.create_glue_table
  source = "../glue/table"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  table_name                     = local.table_name
  aws_glue_catalog_database_name = var.measurement_samples_glue_catalog_database.name
  s3_location                    = local.s3_location
  glue_schema_columns            = local.glue_schema_columns
  partition_keys                 = var.partition_keys
  partitioning_lambda_version    = var.partitioning_lambda_version
}
