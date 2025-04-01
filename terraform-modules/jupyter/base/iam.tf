data "aws_iam_policy_document" "ecs_tasks_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "ecs_tasks_execution_role" {
  name               = "${local.name_prefix}_ecs_task_execution_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume_role.json
  tags               = local.tags.default
}

resource "aws_iam_role" "ecs_taks_role" {
  name               = "${local.name_prefix}_ecs_task_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume_role.json
  tags               = local.tags.default
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_role_allow_s3_full_access" {
  role       = aws_iam_role.ecs_taks_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_role_allow_athena_full_access" {
  role       = aws_iam_role.ecs_taks_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

resource "aws_iam_role_policy_attachment" "ecs_tasks_execution_role" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "read_access_key_secret" {
  name   = "${local.name_prefix}_read_access_key_secret"
  policy = jsonencode(
    {
      Version : "2012-10-17",
      Statement : [
        {
          Sid : "",
          Effect : "Allow",
          Action : "secretsmanager:GetSecretValue",
          Resource : aws_secretsmanager_secret.read_reports.arn
        }
      ]
    }
  )
  tags = local.tags.default
}

resource "aws_iam_role_policy_attachment" "read_access_key_secret" {
  role       = aws_iam_role.ecs_tasks_execution_role.name
  policy_arn = aws_iam_policy.read_access_key_secret.arn
}

resource "aws_iam_role" "lambda" {
  name = "${local.name_prefix}_lambda_default"

  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.allow_run_ecs_task.arn
  ]
  tags = local.tags.default
}

resource "aws_iam_policy" "allow_run_ecs_task" {
  name   = "${local.name_prefix}_allow_run_ecs_task"
  policy = jsonencode(
    {
      Version : "2012-10-17",
      Statement : [
        {
          Sid : "",
          Effect : "Allow",
          Action : "ecs:RunTask",
          #          todo: consider if this is a security threat
          Resource : "*"
        },
        {
          Sid : "",
          Effect : "Allow",
          Action : "iam:PassRole",
          Resource : [
            aws_iam_role.ecs_taks_role.arn,
            aws_iam_role.ecs_tasks_execution_role.arn
          ]
        }
      ]
    }
  )
  tags = local.tags.default
}


resource "aws_iam_user" "read_reports" {
  name = "${local.name_prefix}_read_reports_user"
  tags = local.tags.default
}

resource "aws_iam_user_policy" "read_reports" {
  policy = jsonencode(
    {
      Version : "2012-10-17",
      Statement : [
        {
          Sid : "",
          Effect : "Allow",
          Action : "s3:GetObject",
          Resource : "${module.reports.aws_s3_bucket.arn}/*"
        }
      ]
    }
  )
  user = aws_iam_user.read_reports.name
}

resource "aws_iam_access_key" "read_reports" {
  user = aws_iam_user.read_reports.name
}
