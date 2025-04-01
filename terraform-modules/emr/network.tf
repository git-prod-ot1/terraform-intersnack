locals {
  communication_port = 18888
}

resource "aws_security_group" "engine" {
  name        = "${local.name_prefix}_emr_studio_engine"
  description = "Security group for emr studio engine"
  vpc_id      = var.vpc_id

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_emr_studio_engine"
  })
}

resource "aws_security_group_rule" "engine" {
  security_group_id        = aws_security_group.engine.id
  type                     = "ingress"
  protocol                 = "TCP"
  from_port                = local.communication_port
  to_port                  = local.communication_port
  source_security_group_id = aws_security_group.workspace.id
}

resource "aws_security_group" "workspace" {

  name        = "${local.name_prefix}_emr_studio_workspace"
  description = "Security group for emr studio workspace"
  vpc_id      = var.vpc_id

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_studio_workspace"
  })
}

resource "aws_security_group_rule" "workspace" {
  security_group_id        = aws_security_group.workspace.id
  type                     = "egress"
  protocol                 = "TCP"
  from_port                = local.communication_port
  to_port                  = local.communication_port
  source_security_group_id = aws_security_group.engine.id
}

resource "aws_security_group" "cluster_service_access" {
  name   = "${local.name_prefix}_service_access"
  vpc_id = var.vpc_id

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_service_access"
  })
}

resource "aws_security_group_rule" "master2service" {
  security_group_id = aws_security_group.cluster_service_access.id

  source_security_group_id = aws_security_group.master.id
  from_port                = 9443
  protocol                 = "TCP"
  to_port                  = 9443
  type                     = "ingress"
}

resource "aws_security_group" "master" {
  name   = "${local.name_prefix}_master"
  vpc_id = var.vpc_id
  tags   = merge(local.tags.default, {
    Name : "${local.name_prefix}_master"
  })
}

resource "aws_security_group" "slave" {
  name   = "${local.name_prefix}_slave"
  vpc_id = var.vpc_id
  tags   = merge(local.tags.default, {
    Name : "${local.name_prefix}_master"
  })
}
