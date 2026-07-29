output "processor_id" {
  description = "Document AI processor ID"
  value       = google_document_ai_processor.layout_parser.id
}

output "processor_name" {
  description = "Document AI processor name"
  value       = google_document_ai_processor.layout_parser.name
}


output "processor_location" {
  description = "Document AI processor location"
  value       = google_document_ai_processor.layout_parser.location
}