locals {
  assign_route53_record = var.route53_zone != null && var.full_domain != null
}

resource "aws_route53_record" "this" {
  count = local.assign_route53_record ? 1 : 0
  provider = aws.network

  zone_id = var.route53_zone.zone_id
  name    = var.full_domain
  type    = "CNAME"
  ttl     = "300"
  records = [aws_elastic_beanstalk_environment.this.endpoint_url]
}
