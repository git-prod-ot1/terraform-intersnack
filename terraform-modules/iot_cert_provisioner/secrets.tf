resource "aws_secretsmanager_secret" "cert" {
  for_each = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  name     = "${local.name_prefix}_${each.key}_cert"
  tags     = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_cert"], {})
  )
}

resource "aws_secretsmanager_secret" "private_key" {
  for_each = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  name     = "${local.name_prefix}_${each.key}_private_key"
  tags     = merge(
    local.tags.default,
    try(local.tags.typed["aws_secretsmanager_secret"], {}),
    try(local.tags.named["aws_secretsmanager_secret"]["${local.name_prefix}_private_key"], {})
  )
}

resource "aws_secretsmanager_secret_version" "cert" {
  for_each      = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  secret_id     = aws_secretsmanager_secret.cert[each.key].id
  secret_string = aws_iot_certificate.this[each.key].certificate_pem
}

resource "aws_secretsmanager_secret_version" "private_key" {
  for_each      = {for data_client_conf in var.data_clients : data_client_conf[0] => data_client_conf}
  secret_id     = aws_secretsmanager_secret.private_key[each.key].id
  secret_string = aws_iot_certificate.this[each.key].private_key
}
