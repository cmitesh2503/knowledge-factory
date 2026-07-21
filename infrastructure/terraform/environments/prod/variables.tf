variable "project_id" {
  description = "GCP Project ID"
  type        = string
}
variable "region" {
  description = "GCP region"
  type        = string
  default     = "asia-south1"
}
variable "environment" {
  description = "Deployment Environment"
  type        = string
}