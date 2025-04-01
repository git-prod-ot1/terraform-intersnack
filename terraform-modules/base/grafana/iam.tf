data "aws_iam_policy_document" "assume_grafana" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = [
        "grafana.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy" "AmazonGrafanaAthenaAccess" {
  name = "AmazonGrafanaAthenaAccess"
}

data "aws_iam_policy" "AmazonTimestreamReadOnlyAccess" {
  name = "AmazonTimestreamReadOnlyAccess"
}

data "aws_iam_policy" "AmazonAthenaFullAccess" {
  name = "AmazonAthenaFullAccess"
}

data "aws_iam_policy" "AmazonGrafanaCloudWatchAccess" {
  name = "AmazonGrafanaCloudWatchAccess"
}

resource "aws_iam_policy" "s3_athena_bucket_access" {
  name   = "${local.name_prefix}_athena_for_grafana"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:GetBucketLocation",
            "s3:GetObject",
            "s3:ListBucket",
            "s3:ListBucketMultipartUploads",
            "s3:ListMultipartUploadParts",
            "s3:AbortMultipartUpload",
            "s3:CreateBucket",
            "s3:PutObject",
            "s3:PutBucketPublicAccessBlock"
          ],
          "Resource" : [
            var.athena_output_bucket.arn,
            "${var.athena_output_bucket.arn}/*"
          ]
        },
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:Get*",
            "s3:List*"
          ]
          "Resource" : [
            "*"
          ]
        }
      ]
    }
  )
}

resource "aws_iam_role" "grafana" {
  name                = "${local.name_prefix}_grafana_role"
  assume_role_policy  = data.aws_iam_policy_document.assume_grafana.json
  managed_policy_arns = concat([
    data.aws_iam_policy.AmazonAthenaFullAccess.arn,
    data.aws_iam_policy.AmazonGrafanaAthenaAccess.arn,
    data.aws_iam_policy.AmazonTimestreamReadOnlyAccess.arn,
    data.aws_iam_policy.AmazonGrafanaCloudWatchAccess.arn,
    aws_iam_policy.s3_athena_bucket_access.arn
  ], var.grafana_extra_policies_arns)
  force_detach_policies = true
}
