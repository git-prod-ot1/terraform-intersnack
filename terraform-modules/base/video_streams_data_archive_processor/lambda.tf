module "videostreams_processor" {
  source = "../../../terraform-modules/lambda"

  unit_name = "videostream_data_archive_processor"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = local.tags

  source_dir  = "${path.module}/lambda"
  iam_role    = aws_iam_role.video_processor_role
  timeout     = var.videostreams_sqs_visibility_timeout_seconds
  memory_size = 320
  environment = {
    STAGE          = terraform.workspace
    DYNAMODB_TABLE = aws_dynamodb_table.videostreams_tasks_table.name
  }

  layers = [
    var.layers.video_stream_data_archiver.arn,
  ]
}
