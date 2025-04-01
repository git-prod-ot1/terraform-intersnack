module "emr_studio" {
  count  = var.workspace_storage == null ? 1 : 0
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags
  unit_name         = var.unit_name

  bucket_name = "studio"
}
