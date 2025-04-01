locals {
  create_errors_bucket = var.errors_bucket_name == null
  errors_bucket_name   = try(module.errors_bucket[0].aws_s3_bucket.bucket, var.errors_bucket_name)
}

module "errors_bucket" {
  count  = local.create_errors_bucket ? 1 : 0
  source = "../../terraform-modules/s3"

  unit_name         = var.unit_name
  aws_user_id       = var.aws_user_id
  bucket_name       = "errors-bucket"
  company_namespace = var.company_namespace
  tags              = local.tags
}
