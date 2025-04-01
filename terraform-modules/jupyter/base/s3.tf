module "reports" {
  source = "../../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name = var.unit_name
}

module "notebooks" {
  source            = "../../s3"
  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  bucket_name       = "${var.unit_name}-notebooks"
  enable_versioning = true
}
