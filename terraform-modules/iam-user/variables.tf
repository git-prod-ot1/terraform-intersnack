variable "user_name" {
  type = string
  default = null
}

variable "policies" {
  type = list(object({
    name=string
    statements=list(any)
  }))
}

variable "permissions_managed" {
  type = list(string)
  description = "A list of ARNs for managed policies"
  default = []
}
