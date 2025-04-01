module "this" {
  source = "../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  unit_name         = var.unit_name
  tags              = local.tags

  function_name_suffix = "message_transformer"

  source_dir = "${path.module}/lambda/src"
  watch      = [
    "${path.module}/lambda/src/message_transformer.py",
    "${path.module}/lambda/src/metrics_collector.py",
  ]
  handler = "src/main.lambda_handler"

  environment = {
    TOPIC_PARTITIONS_FROM_IOT_STR = var.glue_partitions_from_iot_rule_sql
    SEND_CLIENT_METRICS           = var.send_client_metrics
    SEND_FACTORY_METRICS          = var.send_factory_metrics
  }

  timeout     = 60
  memory_size = 256
}
