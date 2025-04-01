module "video_stream_data_archive_dispatcher" {
  count = var.enable_video_streams_data_dispatcher ? 1 : 0

  source = "./video_stream_data_archive_dispatcher"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name
  tags              = local.tags

  factory_short                             = var.factory_short
  aws_sns_topic_factory                     = aws_sns_topic.factory
  aws_iam_lambda_role                       = var.base.aws_iam_lambda_role
  aws_iam_role_firehose                     = module.iot2s3.aws_iam_role_firehose
  aws_s3_bucket_measurement_samples         = var.base.measurement_samples_bucket
  measurement_samples_glue_catalog_database = var.base.measurement_samples_glue_catalog_database
  base_widgets_length                       = local.base_widgets_length
  last_widgets_y_pos                        = local.last_widgets_y_pos
  widget_height                             = local.widget_height
  aws_s3_bucket_s3_video_feed               = var.base.aws_s3_bucket_s3_video_feed
  sns_topic_arn                             = aws_sns_topic.factory.arn
  layers                                    = var.layers
  aws_dynamodb_table                        = var.video_stream_aws_dynamodb_table
  aws_sqs_queue                             = var.video_streams_aws_sqs_queue
  required_streams                          = var.required_active_video_stream_names
  custom_video_prefix                       = var.custom_video_prefix
}
