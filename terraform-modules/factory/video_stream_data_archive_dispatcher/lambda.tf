module "dispatcher_lambda" {
  source = "../../../terraform-modules/lambda"

  aws_user_id          = var.aws_user_id
  company_namespace    = var.company_namespace
  tags                 = local.tags
  function_name_suffix = "videostream_data_archive_dispatcher"

  unit_name  = var.unit_name
  source_dir = "${path.module}/lambda"
  watch      = [
    "${path.module}/lambda/main.py",
  ]

  memory_size = 128
  timeout     = 175
  iam_role    = aws_iam_role.video_dispatcher_role
  layers      = [
    var.layers.video_stream_data_archiver.arn,
  ]
  environment = {
    COMPANY_NAMESPACE            = var.company_namespace
    FACTORY                      = var.factory_short
    STAGE                        = terraform.workspace
    FRAGMENTS_GAP_ALLOWED_MILLIS = 120
    VIDEO_MAX_LENGTH_IN_SECONDS  = 90
    MAX_LIST_ATTEMPTS            = 5
    BUCKET_NAME                  = var.aws_s3_bucket_s3_video_feed.id
    INDEX_FIREHOSE_NAME          = aws_kinesis_firehose_delivery_stream.video_index.name
    PROCESS_WAIT_SECONDS         = 90
    LAMBDA_TIMEOUT               = 15000
    DYNAMODB_TABLE               = var.aws_dynamodb_table.name
    QUEUE_URL                    = var.aws_sqs_queue.url
    CUSTOM_VIDEO_PREFIX          = var.custom_video_prefix
  }
}

