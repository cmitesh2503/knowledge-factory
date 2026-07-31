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
  description = "Cloud Run Function name"

  value = google_cloudfunctions2_function.pdf_ingestion.name
}

output "service_uri" {
  description = "Cloud Run Function URI"

  value = google_cloudfunctions2_function.pdf_ingestion.service_config[0].uri
}

output "service_account" {
  description = "Cloud Run Function service account"

  value = google_cloudfunctions2_function.pdf_ingestion.service_config[0].service_account_email
}