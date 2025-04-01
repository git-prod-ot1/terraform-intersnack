locals {
  policies           = {
    for policy_index, start_id in range(0, var.no_of_clients, var.clients_per_policy) : policy_index+1 =>
    [
      for client_no in range(start_id, start_id + var.clients_per_policy < var.no_of_clients? start_id + var.clients_per_policy : var.no_of_clients, 1) :
      client_no
    ]
  }
}


resource "aws_iot_policy" "clients" {
  for_each = local.policies
  name     = "${local.name_prefix}_clients_${each.key}"

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
            "arn:aws:iot:${var.region}:${var.aws_user_id}:client/${local.name_prefix}_${format("%04d", client_number + 1)}"
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


//todo: improve to support sub/receive/publish separately by configuration
resource "aws_iot_policy" "read" {
  name   = "${local.name_prefix}_permissions"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "iot:Receive",
            "iot:Subscribe",
          ],
          "Resource" : [
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${var.topic}",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topic/${var.topic}/*",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${var.topic}",
            "arn:aws:iot:${var.region}:${var.aws_user_id}:topicfilter/${var.topic}/*",
          ]
        }
      ]
    }
  )
}
