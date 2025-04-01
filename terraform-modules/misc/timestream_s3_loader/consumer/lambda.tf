module "lambda" {
  source = "../../../../terraform-modules/lambda_docker"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  permissions = [
    {
      name : local.name_prefix
      policy : {
        "Version" : "2012-10-17",
        "Statement" : [
          {
            "Effect" : "Allow",
            "Action" : [
              "s3:GetObject",
              "s3:ListBucket"
            ],
            "Resource" : [
              "${var.s3_data_bucket.arn}",
              "${var.s3_data_bucket.arn}/*"
            ]
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "timestream:WriteRecords",
            ],
            "Resource" : [
              "arn:aws:timestream:${var.region}:${var.aws_user_id}:database/${var.target_timestream.database}/table/${var.target_timestream.table}"
            ]
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "timestream:DescribeEndpoints",
            ],
            "Resource" : [
              "*"
            ]
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "sqs:DeleteMessage",
              "sqs:ReceiveMessage",
              "sqs:GetQueueAttributes"
            ],
            "Resource" : var.sqs.arn
          }
        ]
      }
    },
  ]

  environment = {
    STAGE             = terraform.workspace
    COMPANY_NAMESPACE = var.company_namespace
    UNIT_NAME         = var.unit_name
    TIMESTREAM_DB     = var.target_timestream.database
    TIMESTREAM_TABLE  = var.target_timestream.table
  }
  timeout     = 60
  memory_size = 256
  reserved_concurrent_executions = 100
}


resource "aws_lambda_event_source_mapping" "from_sqs" {
  event_source_arn = var.sqs.arn
  function_name    = module.lambda.aws_lambda_function.function_name
  batch_size       = 1
  enabled          = true
}
