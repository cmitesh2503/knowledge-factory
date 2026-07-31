output "bucket_names" {
  value = module.storage.bucket_names
}

output "service_account_emails" {

  value = module.service_accounts.service_account_emails
}

output "firestore_database_name" {

  description = "Firestore database name"

  value = module.firestore.database_name
}

output "firestore_database_id" {

  description = "Firestore database id"

  value = module.firestore.database_id
}

output "workflow_name" {
  description = "Knowledge Factory workflow name"
  value       = module.workflows.workflow_name
}

output "workflow_id" {
  description = "Knowledge Factory workflow ID"
  value       = module.workflows.workflow_id
}

output "document_ai_processor_id" {

  value = module.document_ai.processor_id

}
output "document_ai_processor_name" {

  value = module.document_ai.processor_name

}
output "document_ai_processor_location" {

  value = module.document_ai.processor_location

}

output "function_name" {
  value = module.cloudrun.function_name
}

output "service_uri" {
  value = module.cloudrun.function_uri
}

output "service_account" {
  value = module.cloudrun.service_account_email
}

output "artifacts_bucket_name" {
  description = "Deployment artifacts bucket"

  value = module.storage.artifacts_bucket_name
}