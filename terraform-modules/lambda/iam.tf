locals {
  assign_network = var.vpc_config != null
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  name = "AWSLambdaBasicExecutionRole"
}


resource "aws_iam_policy" "this" {
  for_each = {for permission in toset(var.permissions) : permission.name => permission}

  name   = each.value.name
  policy = jsonencode(each.value.policy)
  tags   = local.tags.default
}

resource "aws_iam_policy" "allow_metrics" {
  name   = "${local.function_name}_AllowPutMetricsCloudwatch"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Action" : "cloudwatch:PutMetricData",
        "Resource" : "*"
      }
    ]
  })
  tags = local.tags.default
}

resource "aws_iam_policy" "allow_network" {
  count  = local.assign_network ? 1 : 0
  name   = "${local.function_name}_AllowNetwork"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Action" : [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AssignPrivateIpAddresses",
          "ec2:UnassignPrivateIpAddresses"
        ],
        "Resource" : "*"
      }
    ]
  })
  tags = local.tags.default
}

resource "aws_iam_role" "lambda" {
  count = var.iam_role == null ? 1 : 0
  name  = "${local.name_prefix}_lambda${local.function_suffix}"

  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = concat(
    [
      data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn,
      aws_iam_policy.allow_metrics.arn,
    ],
    #    splat operator doesn't work https://github.com/hashicorp/terraform/issues/22476
    [for policy in aws_iam_policy.this : policy.arn],
    var.permissions_managed
  )

  force_detach_policies = true

  tags = local.tags.default
}


#resource "aws_lambda_permission" "allow_iot_custom_auth_trigger" {
#  action = "lambda:InvokeFunction"
#  function_name = aws_lambda_function.this.function_name
#  principal = "iot.amazonaws.com"
#  source_arn = aws_iot_authorizer.this.arn
#}
