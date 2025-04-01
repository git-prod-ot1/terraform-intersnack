locals {
  function_suffix = var.function_name_suffix != null ? "_${var.function_name_suffix}" : ""
  function_name   = "${local.name_prefix}${local.function_suffix}"
  watch = concat(["${var.source_dir}/main.py"], var.watch)
  hash = join("", [for f in local.watch : substr(filebase64sha256(f), 1, 10)])
}

data "archive_file" "this" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.root}/lambda/${local.function_name}-${local.hash}.zip"
}

resource "aws_lambda_function" "this" {
  filename      = data.archive_file.this.output_path
  function_name = local.function_name
  role          = var.iam_role == null ? aws_iam_role.lambda[0].arn : var.iam_role.arn
  handler       = "main.lambda_handler"
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_lambda_function"], {}),
    try(local.tags.named["aws_lambda_function"][local.function_name], {})
  )
  layers = var.layers

  source_code_hash = data.archive_file.this.output_base64sha256
  dynamic "vpc_config" {
    for_each = var.vpc_config == null ? [] : [var.vpc_config]
    content {
      security_group_ids = vpc_config.value.security_group_ids
      subnet_ids         = vpc_config.value.subnet_ids
    }
  }
  runtime                        = var.runtime
  timeout                        = var.timeout
  memory_size                    = var.memory_size
  reserved_concurrent_executions = var.reserved_concurrent_executions

  environment {
    variables = merge({
      STAGE             = terraform.workspace
      COMPANY_NAMESPACE = var.company_namespace
      UNIT_NAME         = var.unit_name
      HASH = join("", [for f in local.watch : substr(filebase64sha256(f), 1, 10)])
    },
      var.environment
    )
  }

  lifecycle {
    ignore_changes = [source_code_hash]
  }
}
