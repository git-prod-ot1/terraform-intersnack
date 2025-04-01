resource "aws_secretsmanager_secret" "read_reports" {
  name = "${local.name_prefix}_read_s3"
  tags = local.tags.default
}

resource "aws_secretsmanager_secret_version" "read_reports" {
  secret_id     = aws_secretsmanager_secret.read_reports.id
  secret_string = jsonencode(
  {
    "access_key" : aws_iam_access_key.read_reports.id
    "access_key_secret" : aws_iam_access_key.read_reports.secret
  }
  )
}
