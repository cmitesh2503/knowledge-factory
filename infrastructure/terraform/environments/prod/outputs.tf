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