resource "aws_cloudwatch_log_group" "this" {
  name              = "${local.name_prefix}_logs"
  retention_in_days = var.logs_retention_in_days
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["${local.name_prefix}_logs"], {})
  )
}
