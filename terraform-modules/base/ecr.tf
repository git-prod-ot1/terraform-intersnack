resource "aws_ecr_repository" "kinesis" {
  name                 = "${local.company_name_prefix}_kinesis"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags.default

}

resource "aws_ecr_repository" "recorder" {
  name                 = "${local.company_name_prefix}_recorder"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags.default

}
