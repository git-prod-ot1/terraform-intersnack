resource "aws_cloudwatch_event_rule" "this" {
  name                = local.name_prefix
  description         = "Triggers creating reports for ${var.report_name}"
  schedule_expression = var.report_trigger_cron
  is_enabled          = var.is_enabled
  tags                = local.tags.default
}

resource "aws_cloudwatch_event_target" "this" {
  rule = aws_cloudwatch_event_rule.this.name
  arn  = module.report_lambda.aws_lambda_function.arn
}

resource "aws_lambda_permission" "this" {
  action        = "lambda:InvokeFunction"
  function_name = module.report_lambda.aws_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.this.arn
}
