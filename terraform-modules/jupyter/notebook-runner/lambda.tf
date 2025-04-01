locals {
  report_config = var.is_report == false ? {
    FACTORY = var.factory
  } : {
    REPORT_EXT = var.report_extension
    IS_REPORT  = true
    FACTORY    = var.factory
  }
  teams_config = var.teams == null ? {} : {
    TEAMS_ACTIVITY_TITLE    = coalesce(var.teams.activity_title, var.activity_title)
    TEAMS_ACTIVITY_SUBTITLE = var.teams.activity_subtitle
    TEAMS_ACTIVITY_IMAGE    = var.teams.activity_image
    TEAMS_WEBHOOK_URL       = var.teams.webhook_url
  }
  lailo_config = var.lailo == null ? {} : {
    LAILO_WEBHOOK_URL    = var.lailo.webhook_url
    LAILO_ACTIVITY_TITLE = coalesce(var.lailo.activity_title, var.activity_title)
  }
  telegram_config = var.telegram == null ? {} : {
    TELEGRAM_ACTIVITY_TITLE = coalesce(var.telegram.activity_title, var.activity_title)
    TELEGRAM_CHAT_ID        = var.telegram.chat_id
    TELEGRAM_BOT_TOKEN      = var.telegram.bot_token
  }
  target_time_config = var.report_trigger_local_time == null ? {} : {
    TARGET_LOCAL_TIME = var.report_trigger_local_time
    TARGET_TZ         = var.report_trigger_timezone
  }
}

module "report_lambda" {
  source = "../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  unit_name  = var.unit_name
  source_dir = "${path.module}/lambda/runner"

  memory_size = 256
  timeout     = 90
  iam_role    = var.iam_lambda_role
  layers      = [
    var.layers.pytz.arn
  ]

  environment = merge(
    {
      STAGE           = terraform.workspace
      CLUSTER         = var.ecs_cluster.name
      TASK_DEFINITION = "${aws_ecs_task_definition.runner.id}:${aws_ecs_task_definition.runner.revision}"
      SUBNETS         = join(",", var.subnets.*.id)
      SECURITY_GROUPS = var.ecs_task_security_group.id
      NOTEBOOK_NAME   = var.notebook_name
      ACTIVITY_TITLE  = var.activity_title
    },
    local.report_config,
    local.teams_config,
    local.lailo_config,
    local.telegram_config,
    local.target_time_config,
    var.additional_env_vars
  )
}

