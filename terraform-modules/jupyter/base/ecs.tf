locals {
  default_task_definition = {
    image : "${aws_ecr_repository.runner.repository_url}:latest",
    cpu : 1024,
    memoryReservation : 2048,
    name : "runner",
    networkMode : "awsvpc",
    environment : [
      {
        name : "TARGET_S3_BUCKET",
        value : module.reports.aws_s3_bucket.bucket
      },
      {
        name : "NOTEBOOKS_S3_BUCKET",
        value : module.notebooks.aws_s3_bucket.bucket
      },
      {
        name : "AWS_DEFAULT_REGION",
        value : var.region
      }
    ],
    secrets : [
      {
        name : "ACCESS_KEY_SECRET",
        valueFrom : aws_secretsmanager_secret.read_reports.arn
      }
    ]
    logConfiguration : {
      logDriver : "awslogs",
      options : {
        "awslogs-group" : aws_cloudwatch_log_group.runner.name,
        "awslogs-region" : var.region,
        "awslogs-stream-prefix" : "ecs"
      }
    },
    mountPoints : [
      {
        "sourceVolume" : "workspace",
        "containerPath" : "/workspace"
      }
    ],
    readonlyRootFilesystem : true
  }
}


resource "aws_ecs_cluster" "this" {
  name = local.name_prefix
  tags = local.tags.default
}

resource "aws_ecs_task_definition" "runner" {
  family                   = "${local.name_prefix}_runner"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.ecs_taks_role.arn
  execution_role_arn       = aws_iam_role.ecs_tasks_execution_role.arn
  cpu                      = 1024
  memory                   = 4096
  volume {
    name = "workspace"
  }
  container_definitions = jsonencode([
    local.default_task_definition
  ])

  tags = local.tags.default
}

resource "aws_security_group" "runner" {
  name        = "${local.name_prefix}_runner"
  description = "Security group for notebook runner"
  vpc_id      = var.vpc.id

  ingress {
    description = "Incoming TCP"
    from_port   = 80
    to_port     = 80
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outgoing anything"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_runner"
  })
}
