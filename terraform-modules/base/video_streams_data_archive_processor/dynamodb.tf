resource "aws_dynamodb_table" "videostreams_tasks_table" {
  name = "${local.company_name_prefix}_videostreams"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }

  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = true
  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_dynamodb_table"], {}),
    try(local.tags.named["aws_dynamodb_table"]["${local.company_name_prefix}_videostreams"], {})
  )
}
