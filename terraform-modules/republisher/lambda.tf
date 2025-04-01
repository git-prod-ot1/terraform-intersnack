data "aws_iot_endpoint" "default" {
  endpoint_type = "iot:Data-ATS"
}

module "republish_lambda" {
  source = "../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  unit_name         = var.unit_name
  tags              = local.tags

  function_name_suffix = "republisher"
  permissions_managed  = [
    aws_iam_policy.republish_lambda_policy.arn
  ]

  source_dir = "${path.module}/lambda/"
  watch      = [
    "${path.module}/lambda/aws_root.pem",
    "${path.module}/lambda/case_insensitive_dict.py",
  ]

  environment = {
    REFERENCE_TABLES_BUCKET = var.reference_table_bucket
    UNIT_NAME               = var.unit_name
    STAGE                   = terraform.workspace
    COMPANY_NAMESPACE       = var.company_namespace
    IOT_ENDPOINT            = data.aws_iot_endpoint.default.endpoint_address
  }

  memory_size = 256
  timeout     = 120

  layers = [
    var.layers.mqtt.arn,
  ]
}

resource "aws_lambda_event_source_mapping" "kinesis2lambda" {
  event_source_arn  = var.kinesis_data_stream.arn
  function_name     = module.republish_lambda.aws_lambda_function.arn
  starting_position = "LATEST"

  batch_size                    = 4
  parallelization_factor        = 10
  maximum_record_age_in_seconds = 180
}
