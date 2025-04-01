resource "aws_secretsmanager_secret" "password" {
  name = "${local.name_prefix}_rds_password"
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_rds_password"], {})
  )
}

resource "aws_secretsmanager_secret_version" "password" {
  secret_id     = aws_secretsmanager_secret.password.id
  secret_string = random_password.this.result
}
