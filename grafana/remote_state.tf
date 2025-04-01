data "terraform_remote_state" "main" {
  backend = "s3"
  config  = {
    bucket  = "iscf-terraform-1741343236"
    region  = var.region
    key     = "terraform/terraform.tfstate"
    role_arn = var.role_arn
  }
  workspace = terraform.workspace
}

