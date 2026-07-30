variable "project_id" {
    description = "GCP Project ID"
    type        = string
}

variable "region" {
    description = "Clounrun deployment Region"
    type        = string
}

variable "service_name" {
    description = "Cloud Run service name"
    type        = string
}

variable "container_image" {
    description = "Docker image URI"
    type        = string
}

variable "service_account_name" {
  description = "Service account ID."
  type        = string
}

variable "ingress" {
  description = "Cloud Run ingress setting."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "allow_unauthenticated" {
  description = "Allow public access."
  type        = bool
  default     = false
}

variable "cpu" {
  description = "CPU allocation."
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation."
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances."
  type        = number
  default     = 5
}

variable "timeout_seconds" {
  description = "Request timeout."
  type        = number
  default     = 300
}

variable "environment_variables" {
  description = "Environment variables."
  type        = map(string)
  default     = {}
}

variable "labels" {
  description = "Resource labels."
  type        = map(string)
  default     = {}
}