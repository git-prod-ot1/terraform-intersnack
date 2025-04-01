data "aws_sqs_queue" "iot_errors" {
  name = "${local.company_name_prefix}_iot_rules_errors"
}
