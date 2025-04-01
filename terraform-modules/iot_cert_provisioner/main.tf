locals {
  max_clients_per_policy        = 4
  data_clients_chunked_policies = tomap({
    for client_configuration in var.data_clients :
    client_configuration[0] => [
      for idx in range(ceil(client_configuration[1]/local.max_clients_per_policy)) :
      [tostring(idx), chunklist(range(1, client_configuration[1] + 1), local.max_clients_per_policy)[idx]]
    ]
  })

  data_clients_flat = flatten([
    for client, chunks in local.data_clients_chunked_policies : [
      for idx, vals in chunks : {
        client = client
        index  = idx
        values = vals[1]
      }
    ]
  ])

  data_clients_map = {
    for item in local.data_clients_flat :
    "${item.client}_${item.index+1}" => item
  }

}

resource "aws_iot_certificate" "this" {
  for_each = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  active   = true
}

resource "aws_iot_policy" "clients" {
  for_each = local.data_clients_map
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
            for client_number in each.value.values :
            "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${join("_", compact([local.company_name_prefix,each.value.client, var.client_id_suffix, format("%04d", client_number)]))}"
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
  for_each = local.data_clients_map
  policy   = aws_iot_policy.clients[each.key].name
  target   = aws_iot_certificate.this[each.value.client].arn
}


resource "aws_iot_policy" "permissions" {
  for_each = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  name     = "${local.name_prefix}_permissions_policy_${each.key}"
  policy   = jsonencode(
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
          "Resource" : flatten(
            [
              for topic_pattern in var.data_topic_patterns :
              [
                "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${replace(topic_pattern,"+", each.key )}",
                "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${replace(topic_pattern,"+", each.key )}",
              ]
            ]
          )
        }
      ]
    }
  )
}

resource "aws_iot_policy_attachment" "permissions" {
  for_each = local.data_clients_map
  policy   = aws_iot_policy.permissions[each.value.client].name
  target   = aws_iot_certificate.this[each.value.client].arn
}


resource "aws_iot_policy_attachment" "extra_permissions" {
  for_each = {
    for pair in setproduct(
      keys(aws_iot_certificate.this),
      var.extra_iot_policy_names
    ) :
    "${pair[0]}:${pair[1]}" => {
      client = pair[0]
      policy = pair[1]
    }
  }
  policy = each.value.policy
  target = aws_iot_certificate.this[each.value.client].arn
}

# resource "aws_iot_policy_attachment" "permissions" {
#   policy = aws_iot_policy.permissions.name
#   target = aws_iot_certificate.this.arn
# }
# resource "aws_iot_policy_attachment" "extra_permissions" {
#   for_each = local.extra_policies
#   policy   = each.key
#   target   = aws_iot_certificate.this.arn
# }


# resource "aws_iot_certificate" "debug" {
#   count  = local.create_debug_client ? 1 : 0
#   active = true
# }
#

#
# resource "aws_iot_policy" "debug" {
#   count  = local.create_debug_client ? 1 : 0
#   name   = "${local.name_prefix}_debug_permissions_policy"
#   policy = jsonencode(
#     {
#       "Version" : "2012-10-17",
#       "Statement" : [
#         {
#           "Effect" : "Allow",
#           "Action" : [
#             "iot:Publish",
#             "iot:Receive",
#             "iot:Subscribe"
#           ],
#           "Resource" : [
#             "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${local.data_topic_name}",
#             "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${local.data_topic_name}/*",
#             "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${local.data_topic_name}",
#             "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${local.data_topic_name}/*"
#           ]
#         },
#         {
#           "Effect" : "Allow",
#           "Action" : [
#             "iot:Connect"
#           ],
#           "Resource" : concat([
#             "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${aws_iot_thing.debug[0].name}"
#           ],
#               local.create_wildcard_debug_client ? [
#               "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${aws_iot_thing.debug[0].name}_*"
#             ] : []
#           )
#         }
#       ]
#     }
#   )
# }
#
# resource "aws_iot_policy_attachment" "extra_debug" {
#   for_each = local.create_debug_client ? local.extra_policies : {}
#   policy   = each.key
#   target   = aws_iot_certificate.debug[0].arn
# }
#
# resource "aws_iot_policy_attachment" "debug" {
#   count  = local.create_debug_client ? 1 : 0
#   policy = aws_iot_policy.debug[0].name
#   target = aws_iot_certificate.debug[0].arn
# }
#

#
# resource "aws_iot_policy_attachment" "custom_certificate_clients" {
#   for_each = var.iot_certificate == null ? {} : local.policies
#   policy   = aws_iot_policy.clients[each.key].name
#   target   = var.iot_certificate.arn
# }
#
