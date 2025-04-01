locals {
  glue_schema_columns = concat(var.glue_schema_columns, var.glue_schema_extension_columns)
}
