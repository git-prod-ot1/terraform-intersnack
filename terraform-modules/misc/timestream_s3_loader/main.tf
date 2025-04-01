module "dispatcher" {
  source = "./dispatcher"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "${var.unit_name}_dispatcher"

  sqs = {
    arn = aws_sqs_queue.this.arn,
    url = aws_sqs_queue.this.url
  }

  s3_data_bucket = var.s3_data_bucket
  factory        = var.factory
  tags           = local.tags
}


module "consumer" {
  source = "./consumer"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = "${var.unit_name}_consumer"

  sqs = {
    arn = aws_sqs_queue.this.arn,
    url = aws_sqs_queue.this.url
  }

  target_timestream = {
    database = var.target_timestream.database
    table    = var.target_timestream.table
  }

  s3_data_bucket = var.s3_data_bucket
  tags           = local.tags
}
