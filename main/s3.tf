module "error_data_bucket" {
  count  = terraform.workspace == "dev" ? 1 : 1
  source = "../terraform-modules/s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  bucket_name       = "error-dumps"
  tags              = local.tags
}
