resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = 14
  tags              = merge(
    local.tags.default,
    try(local.tags.typed["aws_cloudwatch_log_group"], {}),
    try(local.tags.named["aws_cloudwatch_log_group"]["/aws/lambda/${local.function_name}"], {})
  )
}
