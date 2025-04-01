resource "aws_cloudwatch_event_rule" "trigger" {
  name        = "${module.lambda.aws_lambda_function.function_name}_trigger"
  description = "Triggers Lambda function every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.trigger.name
  target_id = "${module.lambda.aws_lambda_function.function_name}-target"
  arn       = module.lambda.aws_lambda_function.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.aws_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trigger.arn
}
