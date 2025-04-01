variable "ecs_cluster" {
  type = any
}

variable "app_name" {
  type = string
}

variable "app_version" {
  type = string
}

variable "environment" {
  type    = list(any)
  default = []
}

variable "secrets" {
  type    = list(any)
  default = []
}

variable "cpu" {
  type = number
}

variable "memory" {
  type = number
}

variable "aws_iam_role_ecs_tasks_execution_role" {
  type = any
}

variable "aws_iam_role_ecs_task_role" {
  type        = any
  default     = null
  description = "IAM Role attached to running Fargate container"
}

# used in multiple places - change with care
variable "port" {
  type = number
}

variable "vpc" {
  type = object({
    id = string
  })
}

variable "subnets" {
  type = object({
    private = list(object({ id = string }))
    public  = list(object({ id = string }))
  })
}

variable "lb_listener" {
  type        = any
  description = "A reference to ALB listener object"
}

variable "ecr_repository_url" {
  type        = string
  description = "ECR repository URL"
}


variable "healthcheck_path" {
  type        = string
  description = "Path for a healthcheck"
  default     = "/"
}

variable "ingress_rules" {
  description = "To override default ingress rule, use something else than null"
  default     = null
}

variable "egress_rules" {
  description = "To override default egress rule, use something else than null"
  default     = null
}

variable "load_balancer_security_groups" {
  type        = list(string)
  description = "Security groups of used load balancer"
}

variable "additional_allowed_security_group_ids" {
  type        = list(string)
  default     = []
  description = "If provided it adds security groups allowed to connect to the service"
}


locals {
  app_name        = var.app_name
  app_name_dashed = replace(local.app_name, "_", "-")
}
