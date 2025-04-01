resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/ecs/${local.name_prefix}_${var.app_name}"
  retention_in_days = terraform.workspace=="prod" ? 365 : 30
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["/aws/ecs/${local.name_prefix}_${var.app_name}"], {})
  )
}
