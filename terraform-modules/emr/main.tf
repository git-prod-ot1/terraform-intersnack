locals {
  workspace_storage = coalesce(var.workspace_storage, "s3://${module.emr_studio[0].aws_s3_bucket.bucket}/")
}

resource "aws_emr_studio" "this" {
  auth_mode                   = "IAM"
  default_s3_location         = local.workspace_storage
  engine_security_group_id    = aws_security_group.engine.id
  name                        = var.unit_name
  service_role                = aws_iam_role.studio.arn
  subnet_ids                  = var.subnets_ids
  vpc_id                      = var.vpc_id
  workspace_security_group_id = aws_security_group.workspace.id
}

# temporarily disabled
#resource "aws_emr_cluster" "this" {
#  name         = "${local.name_prefix}_default"
#  applications = [
#    "Hadoop",
#    "Hive",
#    "Hue",
#    "JupyterEnterpriseGateway",
#    "JupyterHub",
#    "Pig",
#  ]
#  log_uri                = local.workspace_storage
#  ebs_root_volume_size   = 10
#  release_label          = "emr-5.36.0"
#  scale_down_behavior    = "TERMINATE_AT_TASK_COMPLETION"
#  service_role           = aws_iam_role.emr.name
#  step                   = []
#  termination_protection = false
#
#  auto_termination_policy {
#    idle_timeout = 3600
#  }
#
#  master_instance_group {
#    instance_count = 1
#    instance_type  = "m5.xlarge"
#    name           = "Master Instance Group"
#    ebs_config {
#      iops                 = 0
#      size                 = 32
#      type                 = "gp2"
#      volumes_per_instance = 2
#    }
#  }
#
#  ec2_attributes {
#    emr_managed_master_security_group = aws_security_group.master.id
#    emr_managed_slave_security_group  = aws_security_group.slave.id
#    instance_profile                  = aws_iam_instance_profile.emr_ec2.arn
#    service_access_security_group     = aws_security_group.cluster_service_access.id
#    subnet_id                         = var.subnets_ids[0]
#  }
#
#  tags = local.tags.default
#
#  depends_on = [
#    aws_security_group_rule.master2service
#  ]
#
#}
