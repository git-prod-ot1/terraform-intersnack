locals {
  dashboard_base = module.kinesis2s3.dashboard_body
  base_widgets_length = length(local.dashboard_base.widgets) - 1
  last_widgets_y_pos = local.dashboard_base.widgets[local.base_widgets_length].y
  widget_height = 6

  dashboard_body = {
    widgets: concat(local.dashboard_base.widgets,[
      {
        type: "metric",
        x: 0,
        y: 32,
        width: 24,
        height: 6,
        properties: {
          view: "timeSeries",
          stacked: false,
          metrics: [
            [ "AWS/IoT", "Success", "ActionType", "Kinesis", "RuleName", aws_iot_topic_rule.this.name ],
            [ ".", "Failure", ".", ".", ".", "." ]
          ],
          region: "eu-central-1",
          title: "Failure/Success rate ${var.unit_name}",
          period: 300
        }
      }
    ])
  }

}

resource "aws_cloudwatch_dashboard" "metrics_dashboard" {
  count = var.create_dashboard ? 1 : 0
  dashboard_name = local.name_prefix
  dashboard_body = jsonencode(local.dashboard_body)
}
