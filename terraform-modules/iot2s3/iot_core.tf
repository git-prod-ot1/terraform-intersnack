locals {
  clients_per_policy = 20
  policies           = {
    for policy_index, start_id in range(0, var.no_of_things, local.clients_per_policy) : policy_index+1 =>
    [
      for client_no in range(start_id, start_id + local.clients_per_policy < var.no_of_things ?
        start_id + local.clients_per_policy : var.no_of_things, 1) :
      client_no
    ]
  }
  data_topic_name              = coalesce(var.topic, "${local.name_prefix}_data")
  rule_topic                   = var.read_topics_below ? "${local.data_topic_name}/#" : local.data_topic_name
  extra_policies               = {for policy in var.iot_policies : policy.name => policy}
  create_debug_client          = (terraform.workspace == "dev" || var.override_debug_client_creation)
  create_wildcard_debug_client = (local.create_debug_client && var.allow_wildcard_debug_client)
  create_iot_type              = var.aws_iot_thing_type == null
  iot_type                     = coalesce(var.aws_iot_thing_type, try(aws_iot_thing_type.this[0], null))
  default_rule_sql             = coalesce(var.iot_rule_sql, "SELECT * as data, clientid() AS clientid FROM '${local.rule_topic}'")
  send_to_kinesis              = !var.aggregate_mode && var.default_action_destination == "KINESIS"
  send_to_firehose             = !var.aggregate_mode && var.default_action_destination == "FIREHOSE"
}

data "aws_iot_endpoint" "default" {
  endpoint_type = "iot:Data-ATS"
}

resource "aws_iot_thing_type" "this" {
  count = local.create_iot_type ? 1 : 0
  name  = local.name_prefix
}

resource "aws_iot_thing" "this" {
  count           = var.no_of_things
  name            = "${local.name_prefix}_${format("%04d", count.index + 1)}"
  thing_type_name = local.iot_type.name
}

resource "aws_iot_thing" "debug" {
  count = local.create_debug_client ? 1 : 0
  name  = "${local.name_prefix}_debug"
}

resource "aws_iot_certificate" "this" {
  active = true
}

resource "aws_iot_certificate" "debug" {
  count  = local.create_debug_client ? 1 : 0
  active = true
}

resource "aws_iot_thing_principal_attachment" "this" {
  count     = var.no_of_things
  principal = aws_iot_certificate.this.arn
  thing     = aws_iot_thing.this[count.index].name
}

resource "aws_iot_thing_principal_attachment" "debug" {
  count     = local.create_debug_client ? 1 : 0
  principal = aws_iot_certificate.debug[0].arn
  thing     = aws_iot_thing.debug[0].name
}

resource "aws_iot_policy" "permissions" {
  name   = "${local.name_prefix}_permissions_policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Publish",
            "iot:Receive"
          ],
          "Resource" : [
            "arn:aws:iot:eu-central-1:${var.aws_user_id}:topic/${local.data_topic_name}",
            "arn:aws:iot:eu-central-1:${var.aws_user_id}:topic/${local.data_topic_name}/*"
          ]
        }
      ]
    }
  )
}

resource "aws_iot_policy" "debug" {
  count  = local.create_debug_client ? 1 : 0
  name   = "${local.name_prefix}_debug_permissions_policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Publish",
            "iot:Receive",
            "iot:Subscribe"
          ],
          "Resource" : [
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${local.data_topic_name}",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${local.data_topic_name}/*",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${local.data_topic_name}",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${local.data_topic_name}/*"
          ]
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Connect"
          ],
          "Resource" : concat([
            "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${aws_iot_thing.debug[0].name}"
          ],
              local.create_wildcard_debug_client ? [
              "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${aws_iot_thing.debug[0].name}_*"
            ] : []
          )
        }
      ]
    }
  )
}

resource "aws_iot_policy_attachment" "extra_debug" {
  for_each = local.create_debug_client ? local.extra_policies : {}
  policy   = each.key
  target   = aws_iot_certificate.debug[0].arn
}

resource "aws_iot_policy_attachment" "debug" {
  count  = local.create_debug_client ? 1 : 0
  policy = aws_iot_policy.debug[0].name
  target = aws_iot_certificate.debug[0].arn
}

resource "aws_iot_policy_attachment" "permissions" {
  policy = aws_iot_policy.permissions.name
  target = aws_iot_certificate.this.arn
}
resource "aws_iot_policy_attachment" "extra_permissions" {
  for_each = local.extra_policies
  policy   = each.key
  target   = aws_iot_certificate.this.arn
}

resource "aws_iot_policy_attachment" "custom_certificate_permissions" {
  count  = var.iot_certificate == null ? 0 : 1
  policy = aws_iot_policy.permissions.name
  target = var.iot_certificate.arn
}

resource "aws_iot_policy_attachment" "custom_certificate_extra_permissions" {
  for_each = var.iot_certificate == null ? {} : local.extra_policies
  policy   = each.key
  target   = var.iot_certificate.arn
}


resource "aws_iot_policy" "clients" {
  for_each = local.policies
  name     = "${local.name_prefix}_clients_policy_${each.key}"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Connect"
          ],
          "Resource" : [
            for client_number in each.value :
            "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${aws_iot_thing.this[client_number].name}"
          ],
          "Condition" : {
            "ForAllValues:StringEquals" : {
              "iot:ConnectAttributes" : [
                "PersistentConnect"
              ]
            }
          }
        }
      ]
    }
  )
}

resource "aws_iot_policy_attachment" "clients" {
  for_each = local.policies
  policy   = aws_iot_policy.clients[each.key].name
  target   = aws_iot_certificate.this.arn
}

resource "aws_iot_policy_attachment" "custom_certificate_clients" {
  for_each = var.iot_certificate == null ? {} : local.policies
  policy   = aws_iot_policy.clients[each.key].name
  target   = var.iot_certificate.arn
}

resource "aws_iot_topic_rule" "this" {
  enabled     = var.default_iot_rule_enabled
  name        = "${local.name_prefix}_rule"
  sql         = local.default_rule_sql
  sql_version = "2016-03-23"

  dynamic "kinesis" {
    for_each = local.send_to_kinesis ? [1]: []
    content {
      partition_key = var.kinesis_partition_key
      role_arn      = aws_iam_role.iot_role.arn
      stream_name   = module.kinesis2s3.kinesis_data_stream.name
    }
  }

  dynamic "firehose" {
    for_each = local.send_to_firehose ? [1] : []
    content {
      delivery_stream_name = module.kinesis2s3.firehose_stream.name
      role_arn             = aws_iam_role.iot_role.arn
    }
  }

  dynamic "republish" {
    for_each = coalesce(try(var.iot_rule_actions.republish, []))
    content {
      role_arn = republish.value.role_arn
      topic    = republish.value.topic
      qos      = republish.value.qos
    }
  }

  error_action {
    dynamic "s3" {
      for_each = var.iot_rule_sql != null ? [1] : []
      content {
        bucket_name = var.iot_error_actions_bucket.bucket
        key         = "${var.unit_name}/$${newuuid()}"
        role_arn    = aws_iam_role.iot_error_actions.arn
      }
    }

    dynamic "sqs" {
      for_each = var.iot_rule_sql == null ? [1] : []
      content {
        queue_url   = data.aws_sqs_queue.iot_errors.url
        role_arn    = aws_iam_role.iot_error_actions.arn
        use_base64  = true
      }
    }
  }
}
