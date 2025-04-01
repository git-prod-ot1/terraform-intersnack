output "certificate_validation" {
  value = null
  precondition {
    condition     = (var.certificate_arn != null || (var.route53_zone != null && var.full_domain != null )) || !var.enable_ssl
    error_message = "Either certificate_arn or route53_zone and full_domain have to be set"
  }
}

variable "subnets" {
  type = object({
    private = list(object({ id = string, availability_zone = string }))
    public  = list(object({ id = string, availability_zone = string }))
  })
}

variable "solution_stack_name" {
  type        = string
  description = "Stack name ex. 64bit Amazon Linux 2 2.4.3 running .NET Core"
}

variable "additional_settings" {
  type = list(object({
    name : string,
    namespace : string,
    value : string,
  }))
  default = []
}

variable "certificate_arn" {
  type        = string
  default     = null
  description = "ARN of a certificate for SSL, if not provided, default is created"
}

variable "vpc" {
  type        = any
  description = "Reference to VPC resource"
}


variable "route53_zone" {
  type        = any
  description = "Reference to Route53 hosted zone resource"
  default     = null
}

variable "full_domain" {
  type    = string
  default = null
}

variable "logs_retention_in_days" {
  type        = number
  description = "Retention in days for cloudwatch logs"
  default     = 30
}

variable "access_logs_bucket" {
  type        = any
  description = "A reference to a bucket used for saving access logs to application load balancer"
}

variable "ec2_extra_policies_arns" {
  type        = list(string)
  default     = []
  description = "A list of extra policies arns that should be applied to EC2 instance"
}

variable "instance_type" {
  type        = string
  default     = "t3.small"
  description = "EC2 instance type."
}

variable "enable_ssl" {
  type        = bool
  default     = true
  description = "Enable port 443 with redirection from 80."
}

variable "managed_actions_enabled" {
  type        = bool
  default     = true
  description = "Enables managed actions like platform update."
}

variable "enable_enhanced_health_reporting" {
  type    = bool
  default = false
}
