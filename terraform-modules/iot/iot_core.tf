locals {
  clients_per_policy = 20
  policies           = {
    for policy_index, start_id in range(0, var.no_of_things, local.clients_per_policy) : policy_index+1 =>
    [
      for client_no in range(start_id, start_id + local.clients_per_policy < var.no_of_things? start_id + local.clients_per_policy : var.no_of_things, 1) :
      client_no
    ]
  }
  data_topic_name              = coalesce(var.topic, "${local.name_prefix}_data")
  extra_policies               = {for policy in var.iot_policies : policy.name => policy}
  create_debug_client          = (terraform.workspace == "dev" || var.override_debug_client_creation)
  create_wildcard_debug_client = (local.create_debug_client && var.allow_wildcard_debug_client)
}

resource "aws_iot_thing_type" "this" {
  name = var.aws_iot_thing_type == null ? local.name_prefix : var.aws_iot_thing_type.name
}


resource "aws_iot_thing" "this" {
  count           = var.no_of_things
  name            = "${local.name_prefix}_${format("%04d", count.index + 1)}"
  thing_type_name = aws_iot_thing_type.this.name
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
    })
}

resource "aws_iot_policy" "permissions" {
  count  = var.permissions_iot_policy == null ? 1 : 0
  name   = "${local.name_prefix}_permissions_policy"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Publish"
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


resource "aws_iot_policy_attachment" "clients" {
  for_each = local.policies
  policy   = aws_iot_policy.clients[each.key].name
  target   = aws_iot_certificate.this.arn
}

resource "aws_iot_policy_attachment" "permissions" {
  policy = var.permissions_iot_policy == null ? aws_iot_policy.permissions[0].name : var.permissions_iot_policy.name
  target = aws_iot_certificate.this.arn
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

resource "aws_iot_policy_attachment" "extra_permissions" {
  for_each = local.extra_policies
  policy   = each.key
  target   = aws_iot_certificate.this.arn
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
