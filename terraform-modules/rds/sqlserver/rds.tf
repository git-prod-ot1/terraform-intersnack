locals {
  db_port                    = 14330
  sql_engine                 = "sqlserver-ex"
  create_option_group        = length(var.rds_backups_s3_buckets) > 0
  major_engine_version       = "15.00"
  aws_db_instance_identifier = coalesce(var.db_instance_name, "${local.name_prefix_dashed}-db01")
}

resource "aws_security_group" "rds_sg" {
  name        = "${local.name_prefix}_rds_sg"
  description = "Security groups for RDS access (temporary public access)"
  vpc_id      = var.vpc.id

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_rds_sg"
  })
}

resource "aws_security_group_rule" "rds_in" {
  count             = var.ingress_allow_all ? 1 : 0
  type              = "ingress"
  from_port         = local.db_port
  to_port           = local.db_port
  protocol          = "tcp"
  security_group_id = aws_security_group.rds_sg.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "rds_out" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  security_group_id = aws_security_group.rds_sg.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "allow_sg_in" {
  count                    = length(var.allow_ingress_from_security_groups) == 0 ? 0 : 1
  type                     = "egress"
  from_port                = local.db_port
  to_port                  = local.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_sg.id
  source_security_group_id = var.allow_ingress_from_security_groups
}

resource "random_password" "this" {
  length           = 16
  special          = true
  override_special = "_%#"
}

resource "aws_db_instance" "this" {
  port                            = local.db_port
  identifier                      = local.aws_db_instance_identifier
  instance_class                  = "db.t3.small"
  engine                          = local.sql_engine
  vpc_security_group_ids          = [aws_security_group.rds_sg.id]
  allocated_storage               = 20
  username                        = "sqladmin"
  password                        = random_password.this.result
  db_subnet_group_name            = aws_db_subnet_group.this.name
  max_allocated_storage           = 1000
  apply_immediately               = true
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.monitoring_role.arn
  deletion_protection             = true
  copy_tags_to_snapshot           = true
  publicly_accessible             = false
  backup_retention_period         = 30
  auto_minor_version_upgrade      = true
  option_group_name               = local.create_option_group ? aws_db_option_group.s3_backup[0].name : null
  enabled_cloudwatch_logs_exports = [
    "error"
  ]

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_db_instance"], {}),
    try(local.tags.named["aws_db_instance"][local.aws_db_instance_identifier], {})
  )
}

resource "aws_db_subnet_group" "this" {
  name       = local.name_prefix
  subnet_ids = var.subnets.private.*.id
  tags       = local.tags.default
}

resource "aws_db_option_group" "s3_backup" {
  name  = "${local.name_prefix_dashed}-db01-backup-option-group"
  count = local.create_option_group ? 1 : 0

  engine_name          = local.sql_engine
  major_engine_version = local.major_engine_version

  option {
    option_name = "SQLSERVER_BACKUP_RESTORE"

    option_settings {
      name  = "IAM_ROLE_ARN"
      value = aws_iam_role.rds_backups_role[0].arn
    }
  }
}
