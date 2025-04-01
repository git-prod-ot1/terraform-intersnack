data "terraform_remote_state" "layers" {
  backend = "s3"
  config = {
    bucket   = "iscf-terraform-1741343236"
    region   = "eu-central-1"
    key      = "layers/terraform/terraform.tfstate"
    role_arn = var.role_arn
  }
  workspace = terraform.workspace
}
