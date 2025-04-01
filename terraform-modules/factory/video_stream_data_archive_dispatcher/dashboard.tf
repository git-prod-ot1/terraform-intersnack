locals {
  kinesis_stream_active_connections = [
    [ { expression: "SEARCH('{AWS/KinesisVideo,StreamName} PutMedia.ActiveConnections ${local.name_prefix_short}', 'Sum', 60)", id: "e1", period: 60, region: "eu-central-1" } ]
  ]
  kinesis_stream_active_connections_overview = [
    [ { expression: "SUM(SEARCH('{AWS/KinesisVideo,StreamName} PutMedia.ActiveConnections ${local.name_prefix_short}', 'Sum', 60))", id: "e1", label: "Active", period: 60, region: "eu-central-1" } ],
    [ { expression: "DATAPOINT_COUNT(SEARCH('{AWS/KinesisVideo,StreamName} PutMedia.ActiveConnections ${local.name_prefix_short}', 'Sum', 60))", id: "e2", label: "Total", period: 60, region: "eu-central-1" } ]
  ]
  kinesis_video_streams_bitrate_metric = [
    [ { expression: "SEARCH('{AWS/KinesisVideo,StreamName} PutMedia.IncomingBytes ${local.name_prefix_short}', 'Sum', 60)", id: "e1", period: 60, region: "eu-central-1", visible: false} ],
    [ { expression: "e1/60*8/1024/1024", id: "e2", label:"" , region: "eu-central-1" } ]
  ]

  widgets = [
    {
      type: "metric",
      x: 0,
      y: var.last_widgets_y_pos + var.widget_height,
      width: 24,
      height: 6,
      properties: {
        metrics: local.kinesis_stream_active_connections,
        view: "singleValue",
        region: "eu-central-1",
        stat: "Maximum",
        period: 60,
        stacked: false,
        setPeriodToTimeRange: false,
        liveData: false,
        singleValueFullPrecision: false,
        title: "${title(var.unit_name)} Streams Status"
      }
    },
    {
      type: "metric",
      x: 0,
      y: var.last_widgets_y_pos + 2 * var.widget_height,
      width: 24,
      height: 6,
      properties: {
        metrics: local.kinesis_video_streams_bitrate_metric,
        view: "timeSeries",
        region: "eu-central-1",
        period: 60,
        stat: "Sum",
        stacked: false,
        yAxis: {
          left: {
            label: "mbps",
            min: 0,
            showUnits: false
          }
        },
        title: "VideoStreams Bitrate"
      }
    },
  ]
}
