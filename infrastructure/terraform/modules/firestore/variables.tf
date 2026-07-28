variable "project_id" {

  description = "Google Cloud Project Id"

  type = string
}

variable "location_id" {

  description = "Firestore database location"

  type = string
}

variable "database_name" {

  description = " Firestore dataase name"

  type = string

  default = "(default)"
}

variable "database_type" {

  description = "Firestore database type"

  type = string

  default = "FIRESTORE_NATIVE"
}