variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "function_name" {
  description = "Cloud Run Function name"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for the function"
  type        = string
}

variable "raw_bucket" {
  description = "Raw input bucket"
  type        = string
}

variable "processed_bucket" {
  description = "Processed output bucket"
  type        = string
}

variable "firestore_database" {
  description = "Firestore database name"
  type        = string
}

variable "document_ai_processor" {
  description = "Document AI processor name"
  type        = string
}

variable "max_chunk_pages" {
  description = "Maximum pages per chunk"
  type        = number
  default     = 25
}