locals {
  create_acm = var.certificate_arn == null && var.full_domain != null
  certificate_arn = var.certificate_arn == null ? try(module.acm[0].arn, null) : var.certificate_arn
}

module "acm" {
  count     = local.create_acm ? 1 : 0
  providers = {
    aws         = aws
    aws.network = aws.network
  }

  source      = "../acm"
  domain_name = var.full_domain

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  zone_id           = var.route53_zone.zone_id
  validation_method = "DNS"
}
