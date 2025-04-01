data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "elb_allow_logs" {
  name   = "${local.name_prefix}_AllowElbCloudwatchLogs"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource" : aws_cloudwatch_log_group.this.arn
        }
      ]
    },
  )
  tags = local.tags.default
}

resource "aws_iam_role" "elb_ec2_role" {
  name                  = "${local.name_prefix}_ELBEC2"
  assume_role_policy    = data.aws_iam_policy_document.ec2_assume_role.json
  force_detach_policies = true
  managed_policy_arns   = concat([
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
    "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker",
    "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier",
    aws_iam_policy.elb_allow_logs.arn
  ],
    var.ec2_extra_policies_arns)
  tags = local.tags.default
}

resource "aws_iam_instance_profile" "elb_ec2_profile" {
  name = "${local.name_prefix}-instance-profile"
  role = aws_iam_role.elb_ec2_role.name
  tags = local.tags.default
}

data "aws_iam_policy_document" "elasticbeanstalk_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["elasticbeanstalk.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "elb_role" {
  name                  = "${local.name_prefix}_ELB"
  assume_role_policy    = data.aws_iam_policy_document.elasticbeanstalk_assume_role.json
  force_detach_policies = true
  managed_policy_arns   = [
    "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth",
    "arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy",
  ]
  tags = local.tags.default
}
