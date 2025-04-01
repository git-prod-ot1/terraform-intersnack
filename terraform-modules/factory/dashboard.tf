locals {
  dashboard_base      = module.iot2s3.dashboard_body
  base_widgets_length = length(local.dashboard_base.widgets) - 1
  last_widgets_y_pos  = local.dashboard_base.widgets[local.base_widgets_length].y
  widget_height       = 6


  dashboard_body = {
    widgets : concat(
    local.dashboard_base.widgets,
    try(var.enable_video_streams_data_dispatcher ? module.video_stream_data_archive_dispatcher[0].dashboard_widgets : tomap(false), []),
    ),
  }
}

resource "aws_cloudwatch_dashboard" "metrics_dashboard" {
  dashboard_name = local.name_prefix

  dashboard_body = jsonencode(local.dashboard_body)
}
