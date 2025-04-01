resource "aws_kms_key" "cloudwatch_sns_key" {
  description             = "KMS Key for SNS Topic Encryption for CloudWatch Alarms"
  enable_key_rotation     = true
  deletion_window_in_days = 10
}

resource "aws_kms_alias" "cloudwatch_sns_key_alias" {
  name          = "alias/${var.company_namespace}/cloudwatch-sns"
  target_key_id = aws_kms_key.cloudwatch_sns_key.id
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key_policy" "cloudwatch_sns_key_policy" {
  key_id = aws_kms_key.cloudwatch_sns_key.id

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Id" : "key-default-1",
      "Statement" : [
        {
          "Sid" : "Enable IAM User Permissions",
          "Effect" : "Allow",
          "Principal" : {
            "AWS" : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
          },
          "Action" : "kms:*",
          "Resource" : "*"
        },
        {
          "Sid" : "Allow CloudWatch to use the key",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : [
              "cloudwatch.amazonaws.com",
              "s3.amazonaws.com"
            ]
          },
          "Action" : [
            "kms:Decrypt",
            "kms:GenerateDataKey*"
          ],
          "Resource" : aws_kms_key.cloudwatch_sns_key.arn
        }
      ]
    }
  )
}
