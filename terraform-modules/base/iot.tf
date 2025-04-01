module "iot" {
  source = "./iot"

  aws_user_id = var.aws_user_id
  company_namespace = var.company_namespace

  errors_bucket = module.iot_rules_actions_logs.aws_s3_bucket
  tags = local.tags
}
