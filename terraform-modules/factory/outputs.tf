output "module_name" {
  value = var.unit_name
}

output "aws_iot_data_topic" {
  value = module.iot2s3.aws_iot_data_topic
}

output "monitoring_iot_data_topic" {
  value = try(module.monitoring[0].data_topic, null)
}

output "data_stream" {
  value = module.iot2s3.kinesis_data_stream
}

output "sns_topic" {
  value = aws_sns_topic.factory
}

output "outputs" {
  value = {
    data_stream_shards = var.data_stream_shards
    data_stream = module.iot2s3.kinesis_data_stream
    iot_data_rule = module.iot2s3.aws_iot_topic_rule.name
    iot_certificate = module.iot2s3.aws_iot_certificate
  }
}

output "metrics" {
  value = {
    iot_incoming_records_metric   = [
      [{ expression: "${var.unit_name}/PERIOD(${var.unit_name})", label: var.unit_name, id: "${var.unit_name}_e", region: var.region }],
      [{ expression: "FILL(${var.unit_name}_raw,0)", label: "Fill missing data for ${var.unit_name}", visible: false, id: var.unit_name, region: var.region }],
      [ "IoTCoreCustom", "Messages.Incoming", "Factory", var.unit_name, { id: "${var.unit_name}_raw", visible: false } ]
    ]
  }
}

output "timestream_tables" {
  value = length(module.kinesis2timestream) > 0 ? module.kinesis2timestream[0].timestream_tables : null
}

output "timestream_table" {
  value = length(module.kinesis2timestream) > 0 ? module.kinesis2timestream[0].timestream_table : null
}

output "message_transform" {
  value = module.iot2s3.transformation_lambda
}

output "message_transform_monitoring" {
  value = length(module.monitoring) > 0 ? module.monitoring[0].transformation_lambda : null
}

output "transformation_lambda" {
  value = module.iot2s3.transformation_lambda
}

output "transformation_lambda_monitoring" {
  value = length(module.monitoring) > 0 ? module.monitoring[0].transformation_lambda : null
}

output "kinesis2timestream_lambda" {
  value = length(module.kinesis2timestream) > 0 ? module.kinesis2timestream[0].timestream_lambda : null
}

output "video_dispatcher_lambda" {
  value = length(module.video_stream_data_archive_dispatcher) > 0 ? module.video_stream_data_archive_dispatcher[0].lambda : null
}

output "factory_short" {
  value = var.factory_short
}
