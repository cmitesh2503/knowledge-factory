resource "google_document_ai_processor" "layout_parser" {
  project      = var.project_id
  location     = var.location
  display_name = var.display_name
  type         = var.processor_type
}