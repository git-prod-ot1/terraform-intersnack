data "aws_iam_policy_document" "elasticmapreduce" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["elasticmapreduce.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ec2" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy" "AmazonElasticMapReduceEditorsRole" {
  name = "AmazonElasticMapReduceEditorsRole"
}

data "aws_iam_policy" "AmazonElasticMapReduceRole" {
  name = "AmazonElasticMapReduceRole"
}

data "aws_iam_policy" "AmazonElasticMapReduceforEC2Role" {
  name = "AmazonElasticMapReduceforEC2Role"
}

data "aws_iam_policy" "AmazonAthenaFullAccess" {
  name = "AmazonAthenaFullAccess"
}


data "aws_iam_policy" "AmazonS3FullAccess" {
  #  todo: we don't want full access!!
  name = "AmazonS3FullAccess"
}

resource "aws_iam_role" "studio" {
  name                = "${local.name_prefix}_studio"
  assume_role_policy  = data.aws_iam_policy_document.elasticmapreduce.json
  managed_policy_arns = [
    data.aws_iam_policy.AmazonElasticMapReduceEditorsRole.arn,
    data.aws_iam_policy.AmazonS3FullAccess.arn
  ]
}

resource "aws_iam_role" "emr" {
  name                = "${local.name_prefix}_emr"
  assume_role_policy  = data.aws_iam_policy_document.elasticmapreduce.json
  managed_policy_arns = [
    data.aws_iam_policy.AmazonElasticMapReduceRole.arn,
  ]
}

resource "aws_iam_role" "emr_ec2" {
  name                = "${local.name_prefix}_emr_ec2"
  assume_role_policy  = data.aws_iam_policy_document.ec2.json
  managed_policy_arns = [
    data.aws_iam_policy.AmazonElasticMapReduceforEC2Role.arn,
    data.aws_iam_policy.AmazonAthenaFullAccess.arn,
  ]
}

resource "aws_iam_instance_profile" "emr_ec2" {
  name = "${local.name_prefix}_emr_ec2"
  role = aws_iam_role.emr_ec2.name
}


