output "function_name" {
  description = "Cloud Run Function name"
  value       = google_cloudfunctions2_function.pdf_ingestion.name
}

output "function_uri" {
  description = "Cloud Run Function URI"
  value       = google_cloudfunctions2_function.pdf_ingestion.service_config[0].uri
}

output "service_account_email" {
  description = "Cloud Run Function service account email"
  value       = google_cloudfunctions2_function.pdf_ingestion.service_config[0].service_account_email
}