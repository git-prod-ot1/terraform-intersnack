data "aws_iam_policy_document" "rds_monitoring_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
  }
}

data "aws_iam_policy" "AmazonRDSEnhancedMonitoringRole" {
  name = "AmazonRDSEnhancedMonitoringRole"
}

resource "aws_iam_role" "monitoring_role" {
  name                = "${local.name_prefix}_monitoring_role"
  assume_role_policy  = data.aws_iam_policy_document.rds_monitoring_role.json
  managed_policy_arns = [
    data.aws_iam_policy.AmazonRDSEnhancedMonitoringRole.arn
  ]
}

data "aws_iam_policy_document" "rds_backups_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "s3_read_write" {
  name  = "${local.name_prefix}_s3_read_write"
  count = length(var.rds_backups_s3_buckets) > 0 ? 1 : 0

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : "s3:*",
          "Resource" : flatten([
            for bucket_name in var.rds_backups_s3_buckets :
            ["arn:aws:s3:::${bucket_name}", "arn:aws:s3:::${bucket_name}/*"]
          ])
        }
      ]
    }
  )
}

data "aws_iam_policy" "AWSBackupServiceRolePolicyForBackup" {
  name = "AWSBackupServiceRolePolicyForBackup"
}

data "aws_iam_policy" "AWSBackupServiceRolePolicyForRestores" {
  name = "AWSBackupServiceRolePolicyForRestores"
}

resource "aws_iam_role" "rds_backups_role" {
  name  = "${local.name_prefix}_rds_backups_role"
  count = length(var.rds_backups_s3_buckets) > 0 ? 1 : 0

  managed_policy_arns = [
    aws_iam_policy.s3_read_write[0].arn,
    data.aws_iam_policy.AWSBackupServiceRolePolicyForBackup.arn,
    data.aws_iam_policy.AWSBackupServiceRolePolicyForRestores.arn,
  ]
  assume_role_policy = data.aws_iam_policy_document.rds_backups_role.json
}
