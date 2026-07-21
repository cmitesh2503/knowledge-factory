variable "bucket_name" {
  description = " Storage bucket name"
  type        = string
}

variable "location" {
  description = "Bucket location"
  type        = string
}

variable "storage_class" {
  description = "Bucket storage class"
  type        = string
  default     = "STANDARD"
}