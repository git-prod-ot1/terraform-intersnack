locals {
  unit_rate = [
    [{ expression: "${var.unit_name}/PERIOD(${var.unit_name})", label: var.unit_name, id: "${var.unit_name}_e", region: "eu-central-1" }],
    [ "IoTCoreCustom", "Messages.Incoming", "Factory", var.unit_name, { id: var.unit_name, visible: false } ]
  ]
  client_rates = [
    [ { expression: "SEARCH('{IoTCoreCustom,ClientId} Messages.Incoming ${local.name_prefix}', 'Sum', 60)", id: "e1", period: 60, region: "eu-central-1", visible: false } ],
    [ { expression: "e1/60", label: "", id: "e2", region: "eu-central-1" } ]
  ]

  iot_core_widgets = [
    {
      type : "metric",
      x : 0,
      y : 0,
      width : 12,
      height : 6,
      properties : {
        metrics : local.unit_rate,
        view : "singleValue",
        region : "eu-central-1",
        stat : "Sum",
        period : 60,
        title : "Message rate messages/s",
        stacked : false
      }
    },
    {
      type : "metric",
      x : 12,
      y : 0,
      width : 12,
      height : 6,
      properties : {
        metrics : local.client_rates,
        view : "timeSeries",
        stacked : false,
        region : "eu-central-1",
        stat : "Sum",
        period : 60,
        title : "Message rate ${var.unit_name}",
        yAxis : {
          left : {
            showUnits : false,
            label : "messages/s"
          }
        }
      }
    }
  ]
  dashboard_body = {
    widgets : try(
      concat(local.iot_core_widgets, module.kinesis_stream[0].kinesis_widgets),
      local.iot_core_widgets)
  }

}

resource "aws_cloudwatch_dashboard" "metrics_dashboard" {
  count = var.create_dashboard ? 1 : 0
  dashboard_name = local.name_prefix
  dashboard_body = jsonencode(local.dashboard_body)
}
