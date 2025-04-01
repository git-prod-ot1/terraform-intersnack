module "measurement_samples_glue" {
  source = "../../../glue/table"

  aws_glue_catalog_database_name = var.measurement_samples_glue_catalog_database.name

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  s3_location       = "s3://${module.measurement_samples.aws_s3_bucket.bucket}/data/"
  table_name        = lower("${var.unit_name}_measurement_samplesdata")
  tags              = local.tags

  glue_schema_columns = [
    {
      name = "datapointid"
      type = "string"
    },
    {
      name = "value"
      type = "string"
    },
    {
      name = "takenat"
      type = "timestamp"
    },
    {
      name = "takenatend"
      type = "timestamp"
    },
    {
      name = "postedat"
      type = "timestamp"
    },
    {
      name = "receivedat"
      type = "timestamp"
    },
    {
      name = "hour"
      type = "string"
    },
    {
      name = "location"
      type = "string"
    },
    {
      name = "sugarbeetid"
      type = "string"
    },
    {
      name = "rowid"
      type = "string"
    },
    {
      name = "fieldid"
      type = "string"
    },
    {
      name = "rownr"
      type = "string"
    },
    {
      name = "algorithm_version"
      type = "string"
    },
    {
      name = "identificator"
      type = "string"
    },
    {
      name = "robot"
      type = "string"
    },
  ]
}
