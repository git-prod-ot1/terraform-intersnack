resource "aws_cloudwatch_log_group" "runner" {
  name              = "/aws/ecs/${local.name_prefix}_runner"
  retention_in_days = 14
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["/aws/ecs/${local.name_prefix}_runner"], {})
  )
}
