locals {
  function_suffix = var.function_name_suffix != null ? "_${var.function_name_suffix}" : ""
  function_name   = "${local.name_prefix}${local.function_suffix}"
}

resource "aws_lambda_function" "this" {
  function_name = local.function_name
  role          = var.iam_role == null ? aws_iam_role.lambda[0].arn : var.iam_role.arn

  image_uri    = "${var.aws_user_id}.dkr.ecr.${var.region}.amazonaws.com/lambda/provided:latest"
  package_type = "Image"
  timeout      = var.timeout
  memory_size  = var.memory_size
  reserved_concurrent_executions = var.reserved_concurrent_executions

  dynamic "image_config" {
    for_each = var.image_config == null ? [] : [var.image_config]
    content {
      working_directory = image_config.value.working_directory
      command           = image_config.value.command
      entry_point       = image_config.value.entry_point
    }
  }


  dynamic "vpc_config" {
    for_each = var.vpc_config == null ? [] : [var.vpc_config]
    content {
      security_group_ids = vpc_config.value.security_group_ids
      subnet_ids         = vpc_config.value.subnet_ids
    }
  }

  ephemeral_storage {
    size = var.ephemeral_storage_size
  }

  environment {
    variables = merge({
      STAGE             = terraform.workspace
      COMPANY_NAMESPACE = var.company_namespace
      UNIT_NAME         = var.unit_name
    }, var.environment)
  }

  lifecycle {
    ignore_changes = [
      image_uri,
    ]
  }

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_lambda_function"], {}),
    try(local.tags.named["aws_lambda_function"][local.function_name], {})
  )
}
