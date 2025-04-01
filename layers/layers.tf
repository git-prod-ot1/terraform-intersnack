module "layers" {
  source            = "../terraform-modules/layers"
  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = var.tags
}


import {
  id = "prod-iscf-lambda-layers"
  to = module.layers.module.lambda_layers.aws_s3_bucket.this
}
