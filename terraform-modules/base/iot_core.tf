resource "aws_iot_thing_type" "litmusedgedevice" {
  name = "${local.company_name_prefix}_LitmusEdgeDevice"
}

resource "aws_iot_logging_options" "this" {
  default_log_level = "ERROR"
  role_arn          = aws_iam_role.iot_logs.arn
}
