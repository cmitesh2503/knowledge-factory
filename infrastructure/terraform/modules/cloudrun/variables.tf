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

#############################################
# Runtime Configuration
#############################################

variable "runtime" {
  description = "Cloud Functions runtime"
  type        = string
  default     = "python312"
}

variable "entry_point" {
  description = "Python function entry point"
  type        = string
  default     = "ingest_pdf"
}

#############################################
# Compute Configuration
#############################################

variable "memory" {
  description = "Available memory"
  type        = string
  default     = "1Gi"
}

variable "timeout_seconds" {
  description = "Function timeout"
  type        = number
  default     = 540
}

variable "max_instance_count" {
  description = "Maximum function instances"
  type        = number
  default     = 5
}

variable "min_instance_count" {
  description = "Minimum function instances"
  type        = number
  default     = 0
}

#############################################
# Networking
#############################################

variable "ingress_settings" {
  description = "Ingress settings"
  type        = string
  default     = "ALLOW_INTERNAL_ONLY"
}

#############################################
# Retry
#############################################

variable "retry_policy" {
  description = "Eventarc retry policy"
  type        = string
  default     = "RETRY_POLICY_RETRY"
}

#############################################
# Deployment Package
#############################################

variable "source_bucket" {
  description = "Bucket containing Cloud Function source archive"
  type        = string
}

variable "source_object" {
  description = "ZIP archive object name"
  type        = string
}