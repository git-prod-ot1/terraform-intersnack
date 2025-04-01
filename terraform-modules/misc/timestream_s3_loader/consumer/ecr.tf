resource "aws_ecr_repository" "this" {
  name                 = local.name_prefix
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_ecr_repository"], {}),
    try(local.tags.named["aws_ecr_repository"]["${local.name_prefix}_consumer"], {})
  )
}
