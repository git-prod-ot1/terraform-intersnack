terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=4.14.0"
    }
    billing = {
      source  = "hashicorp/aws"
      version = "=4.55.0"
    }
  }
}
