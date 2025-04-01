module "lambda" {
  source = "../../../../terraform-modules/lambda"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags
  source_dir        = "${path.module}/lambda"
  runtime = "python3.11"
  permissions = [
    {
      name : local.name_prefix
      policy : {
        Version = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Action = [
              "sqs:SendMessage",
              "sqs:SendMessageBatch"
            ]
            Resource = [
              var.sqs.arn
            ]
          },
          {
            Effect = "Allow"
            Action = [
              "s3:PutObject",
              "s3:GetObject"
            ]
            Resource = [
              "${module.index.aws_s3_bucket.arn}/*"
            ]
          },
          {
            Effect = "Allow"
            Action = [
              "s3:ListBucket",
            ]
            Resource = [
              var.s3_data_bucket.arn,
              module.index.aws_s3_bucket.arn
            ]
          },
        ]
      }
    },
  ]

  environment = {
    STAGE             = terraform.workspace
    COMPANY_NAMESPACE = var.company_namespace
    UNIT_NAME         = var.unit_name
    QUEUE_URL         = var.sqs.url
    INDEX_BUCKET_NAME = module.index.aws_s3_bucket.bucket
    DATA_BUCKET_NAME  = var.s3_data_bucket.bucket
    FACTORY           = var.factory
  }
  timeout     = 50 // do not change (rate is 1 minute!)
  memory_size = 512
  reserved_concurrent_executions = 1

}
