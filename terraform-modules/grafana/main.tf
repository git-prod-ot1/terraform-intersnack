terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "= 1.31.1"
    }
  }
}

provider "grafana" {
  url  = var.workspace_url
  auth = var.auth
}

#resource "grafana_team" "this" {
#  name = "${local.name_prefix}_default"
#
#  members = [
#    "jfrankowski@bytesmith.pl"
#  ]
#}

resource "grafana_data_source" "timestream" {
  count = var.timestream_table != null ? 1 : 0

  name       = "timestream"
  is_default = true
  type       = "grafana-timestream-datasource"

  json_data_encoded = jsonencode({
    authType        = "ec2_iam_role"
    defaultDatabase = local.company_name_prefix
    defaultRegion   = var.region
    defaultTable    = var.timestream_table
  })
}

resource "grafana_data_source" "athena" {
  name       = "Amazon Athena"
  is_default = false
  type       = "grafana-athena-datasource"


  json_data_encoded = jsonencode({
    authType       = "ec2_iam_role"
    defaultRegion  = var.region
    catalog        = "AWSDataCatalog"
    database       = var.athena_database.name
    workgroup      = "primary"
    outputLocation = "s3://${var.athena_output_s3_bucket.id}"
  })
}

resource "grafana_data_source" "redshift" {
  name = "Redshift"
  type = "grafana-redshift-datasource"

  json_data_encoded = jsonencode({})
}

#resource "grafana_data_source_permission" "athena" {
#  datasource_id = grafana_data_source.athena.id
#
#  permissions {
#    team_id    = grafana_team.this.id
#    permission = "Query"
#  }
#}

resource "grafana_dashboard" "this" {
  config_json = file("${path.module}/dashboard.json")
}

#resource "grafana_dashboard_permission" "this" {
#  dashboard_id = grafana_dashboard.this.dashboard_id
#  permissions {
#    team_id    = grafana_team.this.id
#    permission = "View"
#  }
#}
