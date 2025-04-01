variable "subnets" {
  type        = list(any)
  description = "List of subnets, required field is: id"
}

variable "ecs_cluster" {
  type        = any
  description = "Resource of type aws_ecs_cluster (usually created in base report module)"
}

variable "ecs_task_security_group" {
  type        = any
  description = "Resource of type aws_security_group (usually created in base report module)"
}

variable "iam_lambda_role" {
  type        = any
  description = "Resource of type aws_iam_role for lambda triggering the ECS task"
}

variable "report_name" {
  type        = string
  description = "Name of the report"
  default     = null
}

variable "is_report" {
  type        = bool
  description = "Determines if report is created or just notebook is run"
  default     = true
}

variable "report_extension" {
  type        = string
  default     = "pdf"
  description = "Extension used for generated report"
}

variable "notebook_name" {
  type        = string
  description = "Name of the notebook to be executed"
}

variable "factory" {
  type        = string
  description = "Name of a factory a container is located in"
  default     = "N/A"
}

variable "activity_title" {
  type        = string
  description = "Default activity title for integrations"
  default     = ""
}

variable "teams" {
  type = object({
    activity_title    = optional(string)
    activity_subtitle = string
    activity_image    = string
    webhook_url       = string
  })
  default     = null
  description = "Definition for MS Teams Notifications integration"
}

variable "lailo" {
  type = object({
    activity_title = optional(string)
    webhook_url    = string
  })
  default     = null
  description = "Definition for Lailo Bot integration"
}

variable "telegram" {
  type = object({
    activity_title = optional(string)
    bot_token      = string
    chat_id        = string
  })
  default     = null
  description = "Definition for Telegram Bot integration"
}

variable "report_trigger_cron" {
  type        = string
  default     = "cron(0 5,6 * * ? *)"
  description = "CRON expression for triggering report processing"
}

variable "report_trigger_local_time" {
  type        = string
  default     = "07:00"
  description = "Local time for triggering report processing ex. 17:00"
}

variable "report_trigger_timezone" {
  type        = string
  default     = "Europe/Berlin"
  description = "Timezone used for resolving local time for triggering report processing"
}

variable "additional_env_vars" {
  type        = any
  default     = {}
  description = "Additional env variables passed to lambda triggering report run"
}

variable "is_enabled" {
  type    = bool
  default = true
}

variable "layers" {
  type        = any
  description = "Object holding info about globally accessible layers"
}

variable "default_json_container_definition" {
  type        = any
  description = "A task definition with sensible defaults"
}


#todo: make it optional and create within if not provided
variable "task_role_arn" {
  description = "A reference to default task_role_arn"
}

variable "execution_role_arn" {
  description = "A reference to default execution_role_arn"
}
