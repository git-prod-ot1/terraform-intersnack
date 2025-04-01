resource "aws_grafana_workspace" "this" {
  name                     = local.name_prefix
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = [
    "AWS_SSO",
  ]
  permission_type = "SERVICE_MANAGED"

  data_sources = concat([
    "AMAZON_OPENSEARCH_SERVICE",
    "XRAY",
    "CLOUDWATCH",
    "REDSHIFT",
    "ATHENA",
    "TIMESTREAM",
  ], var.grafana_extra_data_sources)

  notification_destinations = [
    "SNS"
  ]

  dynamic "vpc_configuration" {
    for_each = local.enable_vpc_network ? [1] : []
    content {
      security_group_ids = [aws_security_group.this[0].id]
      subnet_ids         = var.subnets.private.*.id
    }
  }

  role_arn = aws_iam_role.grafana.arn
  tags     = var.tags.default
}

