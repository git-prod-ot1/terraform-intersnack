variable "workspace_storage" {
  default = null
  type = string
  description = "S3 location for storage in a form of s3://dev-sw-athena-tests-c72ebb9934df/"
}

variable "vpc_id" {
  type = string
  description = "An ID of a VPC where EMR Studio should be located in"
}

variable "subnets_ids" {
  type = list(string)
  description = "A list of preferably public subnet ids"
}


