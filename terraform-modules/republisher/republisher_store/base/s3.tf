module "measurement_samples" {
  source = "../../../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  bucket_name = "measurement-samples"
}

module "errors_bucket" {
  source = "../../../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags
  bucket_name       = "error-dumps"
}
