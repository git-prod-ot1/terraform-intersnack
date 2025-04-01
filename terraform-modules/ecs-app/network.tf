resource "aws_lb_target_group" "this" {
  name        = "${local.name_prefix_dashed}-${local.app_name_dashed}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc.id
  target_type = "ip"

  deregistration_delay = 60

  health_check {
    path              = var.healthcheck_path
    interval          = 10
    healthy_threshold = 3
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags.default
}
