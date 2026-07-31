
variable "location" {
  description = "Bucket location"
  type        = string
}

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}


variable "buckets" {
  description = "Storage buckets to create"

  type = map(object({
    storage_class = string
  }))

  default = {
    raw = {
      storage_class = "STANDARD"
    }

    processed = {
      storage_class = "STANDARD"
    }

    archive = {
      storage_class = "COLDLINE"
    }

    artifacts = {
      storage_class = "STANDARD"
    }
  }
}