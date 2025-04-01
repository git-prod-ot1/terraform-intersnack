resource "aws_timestreamwrite_database" "this" {
  database_name = local.name_prefix
}
