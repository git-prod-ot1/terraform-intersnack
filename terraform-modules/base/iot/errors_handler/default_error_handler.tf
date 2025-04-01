moved {
  from = module.this
  to   = module.default_error_handler
}

module "default_error_handler" {
  source = "../../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = local.tags

  unit_name = "iot_errors"

  source_dir = "${path.module}/default_error_handler/src"
  handler    = "src/main.lambda_handler"
  runtime    = "python3.11"

  permissions = [
    {
      name : "${local.name_prefix}_iot_errors_AllowSQS"
      policy : {
        Version   = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "sqs:ReceiveMessage",
              "sqs:DeleteMessage",
              "sqs:GetQueueAttributes",
              "sqs:ChangeMessageVisibility"
            ]
            Resource = [
              var.iot_errors_sqs.arn,
            ]
          },
          {
            Effect = "Allow"
            Action = [
              "sqs:SendMessage"
            ]
            Resource = [
              var.iot_errors_sqs_dlq.arn
            ]
          }
        ]
      }
    },
    {
      name : "${local.name_prefix}_iot_errors_AllowKinesis"
      policy : {
        Version   = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "kinesis:PutRecord",
              "kinesis:PutRecords"
            ]
            Resource = [
              "*"
            ]
          },
        ]
      }
    }
  ]
  environment = {
    DLQ_URL = var.iot_errors_sqs_dlq.url
  }
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn        = var.iot_errors_sqs.arn
  function_name           = module.default_error_handler.aws_lambda_function.arn
  batch_size              = 10
  enabled                 = true
  function_response_types = [
    "ReportBatchItemFailures",
  ]
}
