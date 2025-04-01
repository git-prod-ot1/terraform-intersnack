resource "aws_secretsmanager_secret" "this" {
  name = "${local.name_prefix}${local.name_suffix}"
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id     = aws_secretsmanager_secret.this.id
  secret_string = jsonencode(
    {
      "aws_access_key_id" : aws_iam_access_key.this.id,
      "aws_secret_access_key" : aws_iam_access_key.this.secret
    }
  )
}
