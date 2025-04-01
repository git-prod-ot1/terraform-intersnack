resource "aws_kinesis_firehose_delivery_stream" "video_index" {
  name        = "${local.name_prefix}_video_index_delivery_stream"
  destination = "extended_s3"
  tags        = local.tags["default"]

  extended_s3_configuration {
    bucket_arn          = var.aws_s3_bucket_measurement_samples.arn
    buffering_interval  = 60
    buffering_size      = 64
    compression_format  = "UNCOMPRESSED"
    role_arn            = var.aws_iam_role_firehose.arn
    s3_backup_mode      = "Disabled"
    error_output_prefix = "errors/factory=${var.unit_name}/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    prefix              = "data/factory=${var.unit_name}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_video_index_delivery_stream.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_video_index_delivery_stream_s3.name
    }

    data_format_conversion_configuration {
      enabled = true

      input_format_configuration {
        deserializer {

          open_x_json_ser_de {
            case_insensitive                         = true
            column_to_json_key_mappings              = {}
            convert_dots_in_json_keys_to_underscores = false
          }
        }
      }

      output_format_configuration {
        serializer {
          orc_ser_de {
            block_size_bytes                        = 268435456
            bloom_filter_columns                    = []
            bloom_filter_false_positive_probability = 0.05
            compression                             = "SNAPPY"
            dictionary_key_threshold                = 0
            enable_padding                          = false
            format_version                          = "V0_12"
            padding_tolerance                       = 0.05
            row_index_stride                        = 10000
            stripe_size_bytes                       = 67108864
          }
        }
      }

      schema_configuration {
        database_name = var.measurement_samples_glue_catalog_database.name
        region        = "eu-central-1"
        role_arn      = var.aws_iam_role_firehose.arn
        table_name    = "measurement_samplesdata"
        version_id    = "LATEST"
      }
    }
    processing_configuration {
      enabled = false
    }
  }
}
