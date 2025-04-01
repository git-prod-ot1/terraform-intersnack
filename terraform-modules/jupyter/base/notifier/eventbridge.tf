resource "aws_cloudwatch_event_rule" "ecs_task_stopped" {
  name        = "${local.name_prefix}_stopped_task"
  description = "Used to trigger lambda function when ECS Task for reports stops"

  event_pattern = jsonencode({
    source      = ["aws.ecs"],
    detail-type = ["ECS Task State Change"],
    detail      = {
      lastStatus    = ["STOPPED"],
      clusterArn    = [var.ecs_cluster_arn],
      stoppedReason = [
        {
          "prefix" : "Essential container in task exited"
        }
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.ecs_task_stopped.name
  target_id = "InvokeLambda"
  arn       = module.notifier.aws_lambda_function.arn
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.notifier.aws_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ecs_task_stopped.arn
}
