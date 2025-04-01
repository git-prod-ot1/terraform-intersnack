variable "vpc" {
  type = object({
    id = string
  })
}

variable "subnets" {
  type = object({
    private = list(object({ id = string, availability_zone = string }))
    public  = list(object({ id = string, availability_zone = string }))
  })
}


variable "sns_alarms_recipients" {
  type    = list(string)
  default = []
}

variable "role_arn" {
  type = string
}

variable "CreatedBy" {
  type = string
  nullable = false
  description = "Author of changes, in most cases should equal 'terraform', used for tagging purposes"
}

variable "TechnicalOwner" {
  type = string
  nullable = false
  description = "The technical owner of created resources, used for tagging purposes"
}
