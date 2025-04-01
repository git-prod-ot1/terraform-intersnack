provider "grafana" {
  url  = "https://${data.terraform_remote_state.main.outputs.grafana.workspace_url.endpoint}"
  auth = var.grafana_auth
}

module "grafana" {
  source = "../terraform-modules/grafana"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "grafana"
  tags              = local.tags

  workspace_url           = "https://${data.terraform_remote_state.main.outputs.grafana.workspace_url.endpoint}"
  auth                    = var.grafana_auth
  athena_database         = data.terraform_remote_state.main.outputs.grafana.measurement_samples_glue_catalog_database
  athena_output_s3_bucket = data.terraform_remote_state.main.outputs.grafana.aws_s3_bucket_athena_tests
  timestream_table = "arn:aws:timestream:eu-central-1:490004635651:database/prod_iscf/table/prod_iscf_wevelinghoven_kinesis2timestream"
}

