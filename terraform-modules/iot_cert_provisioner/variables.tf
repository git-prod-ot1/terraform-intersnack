variable "create_debug_client" {
  type        = bool
  description = "Decides if additional debug_client should be created for the set of clients"
  default     = false
}


variable "data_topic_patterns" {
  type        = list(string)
  description = "Patterns for topics for permissions"
}


variable "data_clients" {
  description = "Should provide a list of client names with a number of iot clients to create"
  type        = list(tuple([string, number]))
}

variable "client_id_suffix" {
  type=string
  description = "A suffix to be added to each client id to avoid client id duplicates. Should be unique across account"
  default = null
}

variable "extra_iot_policy_names" {
  type = list(string)
  description = "A list of names of the policies in IoT core that should be added to EACH certificate"
  default = []
}
