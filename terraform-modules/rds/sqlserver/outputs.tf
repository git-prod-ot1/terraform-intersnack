output "rds_security_group_id" {
  value = aws_security_group.rds_sg.id
}

output "rds_endpoint" {
  value = aws_db_instance.this.endpoint
}

output "rds_address" {
  value = aws_db_instance.this.address
}

output "rds_secret_arn" {
  value = aws_secretsmanager_secret.password.arn
}

output "rds_arn" {
  value = aws_db_instance.this.arn
}
