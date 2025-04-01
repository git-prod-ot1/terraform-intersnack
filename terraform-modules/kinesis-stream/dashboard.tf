locals {
  kinesis_incoming_bytes =[
    [ { expression: "${var.shard_count} * 1000 * PERIOD(${local.aws_kinesis_stream_data_name})/60 * IF(${local.aws_kinesis_stream_data_name}, 1, 1)", label: "Incoming bytes Limit", id: "e1", color: "#d62728", period: 60, region: var.region, visible: true } ],
    [ { expression: "${local.aws_kinesis_stream_data_name}/1000/PERIOD(${local.aws_kinesis_stream_data_name}) * IF(${local.aws_kinesis_stream_data_name}, 1, 1)", label: "Incoming kB", id: "e2", color: "#2a27d6", period: 60, region: var.region, visible: true} ],
    [ "AWS/Kinesis", "IncomingBytes", "StreamName", local.aws_kinesis_stream_data_name, { id: local.aws_kinesis_stream_data_name, visible: false } ]
  ]
  kinesis_write_provisioned_exceeded = [
    [ "AWS/Kinesis", "WriteProvisionedThroughputExceeded", "StreamName", local.aws_kinesis_stream_data_name ]
  ]
  kinesis_widgets = [
    {
      type : "metric",
      x : 0,
      y : 6,
      width : 12,
      height : 6,
      properties : {
        metrics : local.kinesis_incoming_bytes,
        region : var.region,
        yAxis : {
          left : {
            min : 0
          }
        },
        stat : "Sum",
        title : "Incoming records ${var.unit_name}",
        view : "timeSeries",
        stacked : false,
        period : 60
      }
    },
    {
      type : "metric",
      x : 12,
      y : 6,
      width : 12,
      height : 6,
      properties : {
        metrics : local.kinesis_write_provisioned_exceeded,
        view : "timeSeries",
        stacked : false,
        region : var.region,
        stat : "Sum",
        period : 60,
        title : "Kinesis Write Exceeded on ${local.aws_kinesis_stream_data_name}"
      }
    }
  ]
}
