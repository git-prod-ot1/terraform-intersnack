output "iot_endpoint_address" {
  value = data.aws_iot_endpoint.default.endpoint_address
}

output "aws_s3_bucket_picture_feed" {
  value = module.picture_feed.aws_s3_bucket
}

output "measurement_samples_glue_catalog_database" {
  value = aws_glue_catalog_database.measurement_samples_database
}

output "measurement_samples_glue_table" {
  value = module.measurement_samplesdata.table
}

output "aws_s3_bucket_athena_tests" {
  value = module.athena_tests.aws_s3_bucket
}

output "aws_grafana_workspace" {
  value = var.grafana_enabled ? module.grafana[0].grafana_workspace : null
}

output "aws_timestream_database" {
  value = aws_timestreamwrite_database.this
}

output "measurement_samples_bucket" {
  value = module.measurement_samples.aws_s3_bucket
}

// use only for dependent module
output "base_outputs" {
  value = {
    pliot_arn                 = aws_iam_role.pliot.arn
    litmus_name               = aws_iot_thing_type.litmusedgedevice.name
    aws_iot_thing_type_litmus = aws_iot_thing_type.litmusedgedevice

    measurement_samples_bucket = module.measurement_samples.aws_s3_bucket

    measurement_samples_glue_catalog_database = aws_glue_catalog_database.measurement_samples_database
    measurement_samples_glue_table            = module.measurement_samplesdata.table

    aws_iam_lambda_role = aws_iam_role.lambda

    aws_s3_bucket_picture_feed  = module.picture_feed.aws_s3_bucket
    s3_video_feed_name          = module.video_feed.aws_s3_bucket.bucket
    aws_s3_bucket_s3_video_feed = module.video_feed.aws_s3_bucket

    aws_s3_bucket_athena_tests = module.athena_tests.aws_s3_bucket

    aws_timestreamwrite_database = aws_timestreamwrite_database.this
    sns_topic                    = local.sns_topic
    errors_bucket                = module.errors_bucket.aws_s3_bucket.bucket
  }
}

output "errors_bucket_name" {
  value = module.errors_bucket.aws_s3_bucket.bucket
}

output "iot_error_action_bucket" {
  value = module.iot_rules_actions_logs.aws_s3_bucket
}

output "application_load_balancer_logs_bucket" {
  value = module.alb_logs.aws_s3_bucket
}

output "sns_topic" {
  value = local.sns_topic
}

output "monitoring_samples_glue_table" {
  value = length(module.monitoring) > 0 ? module.monitoring[0].monitoring_samples_glue_table : null
}

output "monitoring_samples_bucket" {
  value = length(module.monitoring) > 0 ? module.monitoring[0].monitoring_samples_bucket : null
}

output "glue_lambda" {
  value = module.glue_base.glue_lambda
}

output "video_stream_processor_lambda" {
  value = length(module.videostreams_data_archive_processor) > 0 ? module.videostreams_data_archive_processor[0].lambda : null
}

output "video_stream_aws_dynamodb_table" {
  value = length(module.videostreams_data_archive_processor) > 0 ? module.videostreams_data_archive_processor[0].aws_dynamodb_table : null
}

output "video_stream_aws_sqs_queue" {
  value = length(module.videostreams_data_archive_processor) > 0 ? module.videostreams_data_archive_processor[0].aws_sqs_queue : null
}

output "sns_kms_arn" {
  value = aws_kms_key.cloudwatch_sns_key.arn
}
