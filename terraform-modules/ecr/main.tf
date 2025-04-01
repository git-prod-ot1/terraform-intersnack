resource "aws_ecr_repository" "this" {
  name                 = var.ignore_name_prefix ? var.unit_name : local.name_prefix
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(
    local.tags.default,
    try(local.tags.typed["aws_ecr_repository"], {}),
    try(local.tags.named["aws_ecr_repository"][local.name_prefix], {})
  )
}

data "aws_ecr_lifecycle_policy_document" "this" {
  rule {
    priority = 1
    description  = "Keep last ${var.alpha_version_count} alpha images"
    selection {
      tag_status        = "tagged"
      tag_pattern_list  = ["*-alpha"]
      count_type        = "imageCountMoreThan"
      count_number      = var.alpha_version_count
    }
    action {
      type = "expire"
    }
  }

  rule {
    priority = 2
    description  = "Keep last ${var.release_version_count} release images"
    selection {
      tag_status        = "tagged"
      tag_pattern_list  = ["*-release"]
      count_type        = "imageCountMoreThan"
      count_number      = var.release_version_count
    }
    action {
      type = "expire"
    }
  }

  rule {
    priority = 3
    description  = "Delete other images after ${var.default_retention_days} days"
    selection {
      tag_status   = "any"
      count_type   = "sinceImagePushed"
      count_unit   = "days"
      count_number = var.default_retention_days
    }
    action {
      type = "expire"
    }
  }
}

resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name
  policy     = data.aws_ecr_lifecycle_policy_document.this.json
}
