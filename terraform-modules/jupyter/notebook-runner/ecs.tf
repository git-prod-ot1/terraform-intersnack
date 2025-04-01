locals {
  task_definition = merge(
    var.default_json_container_definition,
    {
      logConfiguration : {
        logDriver : var.default_json_container_definition.logConfiguration.logDriver
        options : merge(var.default_json_container_definition.logConfiguration.options, {
          "awslogs-stream-prefix" : var.report_name
        })
      },
    }
  )
}


resource "aws_ecs_task_definition" "runner" {
  family                   = local.name_prefix
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = var.task_role_arn
  execution_role_arn       = var.execution_role_arn
  cpu                      = 1024
  memory                   = 4096
  volume {
    name = "workspace"
  }
  container_definitions = jsonencode([local.task_definition])

  tags = local.tags.default
}
