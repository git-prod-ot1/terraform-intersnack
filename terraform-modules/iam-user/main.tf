locals {
  name_suffix = var.user_name == null ? "" : "_${var.user_name}"
}

resource "aws_iam_user" "this" {
  name = "${local.name_prefix}${local.name_suffix}"
  tags = merge(local.tags.default,
    {
      "SEC-IAM.8" = "SUPPRESSED"
    }
  )
}

resource "aws_iam_user_policy_attachment" "managed" {
  for_each = {for index, policy in var.permissions_managed : policy => policy}
  user       = aws_iam_user.this.name
  policy_arn = each.key
}

resource "aws_iam_user_policy" "this" {
  for_each = {for index, policy in var.policies : policy.name => policy}
  name     = "${local.name_prefix}${local.name_suffix}_${each.value.name}"
  user     = aws_iam_user.this.name
  policy   = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : each.value.statements
    }
  )
}

resource "aws_iam_access_key" "this" {
  user = aws_iam_user.this.name
}
