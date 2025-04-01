output "lambda_src_dir" {
  value = "${path.module}/lambda"
}

output "default_ecs_task_definition" {
  value = aws_ecs_task_definition.runner
}

output "ecs_cluster" {
  value = aws_ecs_cluster.this
}

output "ecs_task_security_group" {
  value = aws_security_group.runner
}

output "iam_lambda_role" {
  value = aws_iam_role.lambda
}


output "default_json_container_definition" {
  value = local.default_task_definition
}
output "task_role_arn" {
  value = aws_iam_role.ecs_taks_role.arn
}

output "execution_role_arn" {
  value = aws_iam_role.ecs_tasks_execution_role.arn
}
