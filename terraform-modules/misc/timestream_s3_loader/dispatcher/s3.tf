module "index" {
  source = "../../../../terraform-modules/s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  bucket_name       = "index"

  tags = local.tags
}
