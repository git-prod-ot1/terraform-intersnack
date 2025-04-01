locals {
  factory_partition               = var.factory_partition_override == null ? var.unit_name : var.factory_partition_override
  takenat_partitioning_prefix     = "data/factory=${local.factory_partition}/year=!{partitionKeyFromLambda:year}/month=!{partitionKeyFromLambda:month}/day=!{partitionKeyFromLambda:day}/"
  default_partitioning_prefix     = "data/factory=${local.factory_partition}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
  dynamic_partition_configuration = (var.enable_takenat_partitioning || var.dynamic_partitioning_prefix != null) ? [
    1
  ] : []
  partitioning_prefix          = var.enable_takenat_partitioning ? local.takenat_partitioning_prefix : (var.dynamic_partitioning_prefix == null ? local.default_partitioning_prefix : var.dynamic_partitioning_prefix)
  create_kinesis_stream = var.firehose_source == "KINESIS" && var.enable_kinesis_data_streams
}

moved {
  from = aws_kinesis_stream.data
  to   = module.kinesis_stream[0].aws_kinesis_stream.data
}

module "kinesis_stream" {
  count  = local.create_kinesis_stream ? 1 : 0
  source = "../kinesis-stream"

  aws_user_id       = var.aws_user_id
  company_namespace = var.company_namespace
  unit_name         = var.unit_name

  sns_topic_arn = local.sns_topic.arn

  on_demand_mode = var.on_demand_mode
  shard_count = var.shard_count

  tags = local.tags
}

resource "aws_kinesis_firehose_delivery_stream" "data" {
  name        = "${local.name_prefix}_delivery_stream"
  destination = "extended_s3"
  tags        = local.tags["default"]

  extended_s3_configuration {

    dynamic "dynamic_partitioning_configuration" {
      for_each = local.dynamic_partition_configuration
      content {
        enabled = true
      }
    }

    bucket_arn          = local.measurement_samples_bucket.arn
    buffering_interval  = 60
    buffering_size      = 64
    compression_format  = "UNCOMPRESSED"
    role_arn            = aws_iam_role.firehose.arn
    s3_backup_mode      = "Disabled"
    error_output_prefix = "errors/factory=${local.factory_partition}/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    prefix              = local.partitioning_prefix

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose_delivery_stream.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_delivery_stream_s3.name
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
        database_name = local.measurement_samples_glue_table.database_name
        region        = "eu-central-1"
        role_arn      = aws_iam_role.firehose.arn
        table_name    = local.measurement_samples_glue_table.name
        version_id    = "LATEST"
      }
    }
    processing_configuration {
      enabled = true

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${local.message_transform_lambda.arn}:$LATEST"
        }

        # Changed to non default value (60) to avoid perpetual changes https://github.com/hashicorp/terraform-provider-aws/issues/9827#issuecomment-1103373902
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = "61"
        }
      }

      dynamic "processors" {
        for_each = local.dynamic_partition_configuration
        content {
          type = "RecordDeAggregation"

          parameters {
            parameter_name  = "SubRecordType"
            parameter_value = "JSON"
          }
        }
      }
    }
  }
  dynamic "kinesis_source_configuration" {
    for_each = local.create_kinesis_stream ? [1] : []
    content {
      kinesis_stream_arn = module.kinesis_stream[0].kinesis_data_stream.arn
      role_arn           = aws_iam_role.firehose.arn
    }
  }
}

