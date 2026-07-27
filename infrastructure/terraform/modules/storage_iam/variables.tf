variable "bindings" {

  description = "Bucket IAM bindings"

  type = map(object({
    bucket = string

    role = string

    member = string
  }))
}