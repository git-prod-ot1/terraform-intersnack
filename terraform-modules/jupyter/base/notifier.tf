module "notifier" {
  source = "./notifier"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "${var.unit_name}_notifier"

  ecs_cluster_arn      = aws_ecs_cluster.this.arn
  sns_topic_arn        = local.sns_topic.arn
  sns_kms_arn          = var.sns_kms_arn
  cloudwatch_log_group = aws_cloudwatch_log_group.runner

  tags = local.tags
}
