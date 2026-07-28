variable "project_id" {
  description = "Google cloud project_id"
  type        = string
}

variable "region" {
  description = "workflow region"
  type        = string
}

variable "workflow_name" {
  description = "Workflow name"
  type        = string
}

variable "service_account_email" {
  description = "Workflow service accoutnt"
  type        = string
}

variable "labels" {
  description = "Workflow labels"
  type        = map(string)
  default     = {}
}