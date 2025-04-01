output "iot_endpoint_address" {
  value = module.base.iot_endpoint_address
}

# output "vpc" {
#   value = var.vpc
# }
#
# output "subnets" {
#   value = var.subnets
# }


output "tags" {
  value = local.tags.default
}

output "aws_user_id" {
  value = var.aws_user_id
}

output "region" {
  value = var.region
}

output "company_namespace" {
  value = var.company_namespace
}


output "grafana" {
  value = {
    workspace_url                             = module.base.aws_grafana_workspace
    athena_database                           = module.base.measurement_samples_glue_catalog_database
    aws_s3_bucket_athena_tests                = module.base.aws_s3_bucket_athena_tests
    measurement_samples_glue_catalog_database = module.base.measurement_samples_glue_catalog_database
  }
}
