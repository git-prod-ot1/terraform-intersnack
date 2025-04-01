locals {
  enable_vpc_network = var.vpc != null && var.subnets != null
}

resource "aws_security_group" "this" {
  count  = local.enable_vpc_network ? 1 : 0
  name   = "${local.name_prefix}_grafana_sg"
  vpc_id = var.vpc.id

  ingress {
    description = "Deny all ingress"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = []
  }

  egress {
    description = "Outgoing anything"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags.default, {
    Name : "${local.name_prefix}_grafana_sg"
  })
}
