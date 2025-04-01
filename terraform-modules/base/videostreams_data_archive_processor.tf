moved {
  from = module.videostreams_base
  to   = module.videostreams_data_archive_processor
}

module "videostreams_data_archive_processor" {
  count = var.enable_video_streams_data_processor ? 1 : 0

  source = "./video_streams_data_archive_processor"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  tags              = var.tags
  layers            = var.layers
  sns_topic_arn     = local.sns_topic.arn

}
