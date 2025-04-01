resource "aws_secretsmanager_secret" "cert" {
  name = "${local.name_prefix}_cert"
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_cert"], {})
  )
}

resource "aws_secretsmanager_secret" "private_key" {
  name = "${local.name_prefix}_private_key"
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_private_key"], {})
  )
}

resource "aws_secretsmanager_secret_version" "cert" {
  secret_id     = aws_secretsmanager_secret.cert.id
  secret_string = aws_iot_certificate.this.certificate_pem
}

resource "aws_secretsmanager_secret_version" "private_key" {
  secret_id     = aws_secretsmanager_secret.private_key.id
  secret_string = aws_iot_certificate.this.private_key
}

resource "aws_secretsmanager_secret" "debug_cert" {
  count = local.create_debug_client ? 1 : 0
  name  = "${local.name_prefix}_debug_cert"
  tags  = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_debug_cert"], {})
  )
}

resource "aws_secretsmanager_secret" "debug_private_key" {
  count = local.create_debug_client ? 1 : 0
  name  = "${local.name_prefix}_debug_private_key"
  tags  = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_debug_private_key"], {})
  )
}

resource "aws_secretsmanager_secret_version" "debug_cert" {
  count         = local.create_debug_client ? 1 : 0
  secret_id     = aws_secretsmanager_secret.debug_cert[0].id
  secret_string = aws_iot_certificate.debug[0].certificate_pem
}

resource "aws_secretsmanager_secret_version" "debug_private_key" {
  count         = local.create_debug_client ? 1 : 0
  secret_id     = aws_secretsmanager_secret.debug_private_key[0].id
  secret_string = aws_iot_certificate.debug[0].private_key
}
