module "grafana" {
  count  = var.grafana_enabled ? 1 : 0
  source = "./grafana"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = var.tags

  athena_output_bucket = module.athena_queries_s3.aws_s3_bucket


  vpc     = var.enable_grafana_networking ? var.vpc : null
  subnets = var.enable_grafana_networking ? var.subnets : null

  grafana_extra_data_sources  = var.grafana_extra_data_sources
  grafana_extra_policies_arns = var.grafana_extra_policies_arns
}
