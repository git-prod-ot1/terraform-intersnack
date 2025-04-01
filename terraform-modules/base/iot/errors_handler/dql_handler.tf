module "dlq_handler" {
  source = "../../../lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  region            = var.region
  tags              = local.tags

  unit_name            = "iot_errors_dlq"

  source_dir = "${path.module}/dlq_handler/src"
  handler    = "src/main.lambda_handler"
  runtime    = "python3.11"

  permissions = [
    {
      name : "${local.name_prefix}_iot_errors_dlq_AllowSQS" // todo: we should look here for better name handling I believe
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
              var.iot_errors_sqs_dlq.arn,
            ]
          }
        ]
      }
    },
    {
      name : "${local.name_prefix}_iot_errors_dlq_AllowS3"
      policy : {
        Version   = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "s3:PutObject"
            ]
            Resource = [
              "${var.errors_bucket.arn}/*"
            ]
          }
        ]
      }
    }
  ]
  environment = {
    S3_BUCKET = var.errors_bucket.bucket
  }
}

resource "aws_lambda_event_source_mapping" "dlq_sqs_trigger" {
  event_source_arn                   = var.iot_errors_sqs_dlq.arn
  function_name                      = module.dlq_handler.aws_lambda_function.arn
  batch_size                         = 10
  maximum_batching_window_in_seconds = 60
  enabled                            = true
}
