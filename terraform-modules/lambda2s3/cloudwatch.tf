resource "aws_cloudwatch_event_rule" "lambda_trigger" {
  name                = "${local.name_prefix}_cloudwatch_event"
  description         = "Trigger ${var.unit_name} lambda"
  is_enabled          = var.is_enabled
  schedule_expression = var.schedule_expression
  tags                = local.tags.default
}

resource "aws_cloudwatch_event_target" "lambda_trigger_target" {
  rule = aws_cloudwatch_event_rule.lambda_trigger.name
  arn  = var.input_lambda.arn
}

resource "aws_lambda_permission" "allow_lambda_trigger" {
  action        = "lambda:InvokeFunction"
  function_name = var.input_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}
