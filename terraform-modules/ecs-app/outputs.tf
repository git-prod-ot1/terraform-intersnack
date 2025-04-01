output "aws_lb_target_group" {
  value = aws_lb_target_group.this
}

output "aws_security_group" {
  value = aws_security_group.this
}

output "service_name_port" {
  value = "${aws_ecs_service.this.name}:${var.port}"
}
