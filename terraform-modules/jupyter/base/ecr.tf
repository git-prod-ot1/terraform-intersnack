#to login into docker ecr
#aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 540404055696.dkr.ecr.eu-central-1.amazonaws.com


resource "aws_ecr_repository" "runner" {
  name                 = "${local.name_prefix}_runner"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags.default
}

output "ecr_runner_url" {
  value = aws_ecr_repository.runner.repository_url
}
