locals {
  glue_schema_columns = concat(var.glue_schema_columns, var.glue_schema_extension_columns)
}

module "glue_base" {
  source = "../glue/base"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace

  tags = local.tags
}

resource "aws_glue_catalog_database" "measurement_samples_database" {
  name = "${local.company_name_prefix}_measurement_samples_database"
  tags = local.tags.default
}

module "measurement_samplesdata" {
  source = "../glue/table"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  table_name                     = "measurement_samplesdata"
  aws_glue_catalog_database_name = aws_glue_catalog_database.measurement_samples_database.name
  s3_location                    = "s3://${module.measurement_samples.aws_s3_bucket.bucket}/data/"

  glue_schema_columns         = local.glue_schema_columns
  partitioning_lambda_version = var.partitioning_lambda_version
}

