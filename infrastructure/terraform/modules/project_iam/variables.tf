variable "project_id" {
  description = "The ID of the project in which to create the IAM resources."
  type        = string
}

variable "bindings" {
  description = "IAM bindings"

  type = map(object({
    member = string
    role   = string
  }))
}