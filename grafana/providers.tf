provider "aws" {
  region = var.region
  assume_role {
    role_arn = var.role_arn
  }
}
terraform {
  required_providers {
    aws = {
      version = ">= 5.82.2"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "= 1.31.1"
    }
  }
  backend "s3" {
    bucket = "iscf-terraform-1741343236"
    region = "eu-central-1"
    key    = "terraform/grafana/terraform.tfstate"
  }
}
