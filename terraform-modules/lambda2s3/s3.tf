module "index" {
  count  = var.index_bucket == null ? 1 : 0
  source = "../s3"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  bucket_name = "index"
}
