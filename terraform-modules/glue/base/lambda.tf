module "glue_partitions_updater" {
  source = "../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags
  source_dir        = "${path.module}/lambda/partition_updater"

  iam_role = aws_iam_role.glue_partitions_lambda

  # this is for now calculated together with glue/base! do not change
  function_name_suffix = "glue_partitions_updater"
  environment          = {
    STAGE             = terraform.workspace
    COMPANY_NAMESPACE = var.company_namespace
    UNIT_NAME         = var.unit_name
  }
  timeout     = 300
  memory_size = 256
}

module "glue_partitions_updater_v2" {
  source = "../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags
  source_dir        = "${path.module}/lambda/partition_updater_v2"

  iam_role = aws_iam_role.glue_partitions_lambda

  # this is for now calculated together with glue/base! do not change
  function_name_suffix = "glue_partitions_updater_v2"
  environment          = {
    STAGE             = terraform.workspace
    COMPANY_NAMESPACE = var.company_namespace
  }
  timeout     = 300
  memory_size = 256
}
