
variable "location" {
  description = "Bucket location"
  type        = string
}

variable "buckets"{
    description = "Map of each buckets to create"
    

    type = map(object({
      name           = string
      storage_class  = string
    }))
}