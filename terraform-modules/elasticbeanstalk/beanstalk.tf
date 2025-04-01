locals {
  default_settings = [
    {
      name      = "ELBSubnets"
      namespace = "aws:ec2:vpc"
      value     = join(",", sort(var.subnets.public.*.id))
    },
    {
      name      = "EnvironmentType"
      namespace = "aws:elasticbeanstalk:environment"
      value     = "LoadBalanced"
    },
    {
      name      = "DisableIMDSv1"
      namespace = "aws:autoscaling:launchconfiguration"
      value     = true
    },
    {
      name      = "IamInstanceProfile"
      namespace = "aws:autoscaling:launchconfiguration"
      value     = aws_iam_instance_profile.elb_ec2_profile.name
    },
    {
      name      = "SecurityGroups"
      namespace = "aws:autoscaling:launchconfiguration"
      value     = aws_security_group.env.id
    },
    {
      name      = "InstanceTypes"
      namespace = "aws:ec2:instances"
      value     = var.instance_type
    },
    {
      name      = "LoadBalancerType"
      namespace = "aws:elasticbeanstalk:environment"
      value     = "application"
    },
      var.enable_enhanced_health_reporting ? [
      {
        name      = "SystemType"
        namespace = "aws:elasticbeanstalk:healthreporting:system"
        value     = "enhanced"
      },
    ] : [],
      var.enable_ssl ?
      [
        {
          name      = "ListenerEnabled"
          namespace = "aws:elbv2:listener:default"
          value     = "false"
        },
        {
          name      = "Protocol"
          namespace = "aws:elbv2:listener:443"
          value     = "HTTPS"
        },
        {
          name      = "SSLCertificateArns"
          namespace = "aws:elbv2:listener:443"
          value     = local.certificate_arn
        },
      ] : [
      {
        name      = "ListenerEnabled"
        namespace = "aws:elbv2:listener:default"
        value     = "true"
      },
    ],
      var.managed_actions_enabled ? [
      {
        name      = "ManagedActionsEnabled"
        namespace = "aws:elasticbeanstalk:managedactions"
        value     = "true"
      },
      {
        name      = "PreferredStartTime"
        namespace = "aws:elasticbeanstalk:managedactions"
        value     = "SUN:00:00"
      },
      {
        name      = "UpdateLevel"
        namespace = "aws:elasticbeanstalk:managedactions:platformupdate"
        value     = "minor"
      },
    ] : [
      {
        name      = "ManagedActionsEnabled"
        namespace = "aws:elasticbeanstalk:managedactions"
        value     = "false"
      },
    ],
    {
      name      = "MaxSize"
      namespace = "aws:autoscaling:asg"
      value     = "1"
    },
    {
      name      = "RetentionInDays"
      namespace = "aws:elasticbeanstalk:cloudwatch:logs"
      value     = "7"
    },
    {
      name      = "ServiceRole"
      namespace = "aws:elasticbeanstalk:environment"
      value     = aws_iam_role.elb_role.arn
    },
    {
      name      = "ManagedSecurityGroup"
      namespace = "aws:elbv2:loadbalancer"
      value     = aws_security_group.this.id
    },
    {
      name      = "AccessLogsS3Bucket"
      namespace = "aws:elbv2:loadbalancer"
      value     = var.access_logs_bucket.bucket
    },
    {
      name      = "AccessLogsS3Enabled"
      namespace = "aws:elbv2:loadbalancer"
      value     = true
    },
    {
      name      = "AccessLogsS3Prefix"
      namespace = "aws:elbv2:loadbalancer"
      value     = var.unit_name
    },
    {
      name      = "SecurityGroups"
      namespace = "aws:elbv2:loadbalancer"
      value     = aws_security_group.this.id
    },
    {
      name      = "StreamLogs"
      namespace = "aws:elasticbeanstalk:cloudwatch:logs"
      value     = "true"
    },
    {
      name      = "Subnets"
      namespace = "aws:ec2:vpc"
      value     = join(",", sort(var.subnets.private.*.id))
    },
    {
      name      = "VPCId"
      namespace = "aws:ec2:vpc"
      value     = var.vpc.id
    }
  ]
  settings = concat(flatten(local.default_settings), var.additional_settings)
}

resource "aws_elastic_beanstalk_application" "this" {
  name        = local.name_prefix
  description = local.name_prefix
  tags        = local.tags.default
}

resource "aws_security_group" "this" {
  name = "${local.name_prefix}_ebs_sg"

  vpc_id = var.vpc.id
  ingress {
    description = "Incoming TCP"
    from_port   = 80
    to_port     = 80
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Incoming TCP HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outgoing anything"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_ebs_sg"
  })
}

resource "aws_security_group" "env" {
  name = "${local.name_prefix}_env"

  vpc_id = var.vpc.id
  ingress {
    description     = "Incoming TCP"
    from_port       = 80
    to_port         = 80
    protocol        = "TCP"
    security_groups = [aws_security_group.this.id]
  }

  egress {
    description = "Outgoing anything"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_env_sg"
  })
}

resource "aws_elastic_beanstalk_environment" "this" {
  name                = "${local.name_prefix_dashed}-env"
  application         = aws_elastic_beanstalk_application.this.name
  solution_stack_name = var.solution_stack_name

  dynamic "setting" {
    for_each = local.settings
    content {
      name      = setting.value.name
      namespace = setting.value.namespace
      value     = setting.value.value
    }
  }

  lifecycle {
    ignore_changes = [
    solution_stack_name
    ]
  }

  tags = local.tags.default
}

resource "aws_lb_listener" "http2https" {
  count             = var.enable_ssl ? 1 : 0
  load_balancer_arn = aws_elastic_beanstalk_environment.this.load_balancers[0]
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
  tags = local.tags.default
}
