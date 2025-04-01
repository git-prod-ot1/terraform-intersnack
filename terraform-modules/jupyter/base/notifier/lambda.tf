module "notifier" {
  source = "../../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  unit_name  = var.unit_name
  source_dir = "${path.module}/lambda/"

  memory_size = 256
  timeout     = 90
  iam_role    = aws_iam_role.lambda
  environment = merge(
    {
      STAGE         = terraform.workspace,
      SNS_TOPIC_ARN = var.sns_topic_arn,
    },
  )
}
