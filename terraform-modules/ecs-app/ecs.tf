locals {
  default_ingress_rules = [
    {
      protocol        = "tcp"
      from_port       = 80
      to_port         = var.port
      security_groups = var.load_balancer_security_groups
    },
    {
      protocol        = "tcp"
      from_port       = 443
      to_port         = 443
      security_groups = var.load_balancer_security_groups
    }
  ]

  default_egress_rules = [
    {
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
  ingress_rules = var.ingress_rules == null ? local.default_ingress_rules : var.ingress_rules
  egress_rules  = var.egress_rules == null ? local.default_egress_rules : var.egress_rules
}


resource "aws_ecs_task_definition" "this" {
  family                   = "${local.name_prefix}_${var.app_name}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = var.aws_iam_role_ecs_task_role != null ? var.aws_iam_role_ecs_task_role.arn : null
  execution_role_arn       = var.aws_iam_role_ecs_tasks_execution_role.arn
  cpu                      = var.cpu
  memory                   = var.memory
  volume {
    name = "app"
  }
  container_definitions    = jsonencode([
    {
      image : "${var.ecr_repository_url}:${var.app_version}",
      cpu : var.cpu,
      memory : var.memory,
      name : var.app_name,
      networkMode : "awsvpc",
      portMappings : [
        {
          containerPort : var.port,
          hostPort : var.port
        },
        {
          containerPort : 443,
          hostPort : 443
        }
      ],
      environment : var.environment,
      secrets : var.secrets,
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : aws_cloudwatch_log_group.this.name,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      },
      readonlyRootFilesystem : true,
      mountPoints : [
        {
          sourceVolume : "app",
          containerPath : "/app",
          readOnly : false
        }
      ]
    }
  ])
}

resource "aws_security_group" "this" {
  name   = "${local.name_prefix}_${var.app_name}_security_group"
  vpc_id = var.vpc.id

  dynamic "ingress" {
    for_each = {for idx, ingress in  local.ingress_rules : idx => ingress}
    content {
      protocol        = ingress.value.protocol
      from_port       = ingress.value.from_port
      to_port         = ingress.value.to_port
      security_groups = concat(try(coalesce(ingress.value.security_groups, []), []), var.additional_allowed_security_group_ids)
      cidr_blocks     = try(coalesce(ingress.value.cidr_blocks, []), [])
    }
  }

  dynamic "egress" {
    for_each = {for idx, egress in local.egress_rules : idx => egress}
    content {
      protocol        = egress.value.protocol
      from_port       = egress.value.from_port
      to_port         = egress.value.to_port
      security_groups = try(coalesce(egress.value.security_groups, []), [])
      cidr_blocks     = try(coalesce(egress.value.cidr_blocks, []), [])
    }
  }
}

resource "aws_ecs_service" "this" {
  name            = "${local.name_prefix}_${var.app_name}"
  cluster         = var.ecs_cluster.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.this.id]
    subnets         = var.subnets.private.*.id
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.id
    container_name   = var.app_name
    container_port   = var.port
  }

  depends_on = [var.lb_listener]

  lifecycle {
    #    comment out if changes to task definition are required
    ignore_changes = [
      task_definition
    ]
  }
}
