module "lambda_layers" {
  source = "../s3"
  aws_user_id = var.aws_user_id
  company_namespace = var.company_namespace
  tags = local.tags

  bucket_name = "lambda-layers"
}
