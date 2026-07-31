#############################################
# Cloud Functions Gen2
# PDF Ingestion Function
#############################################

resource "google_cloudfunctions2_function" "pdf_ingestion" {

  name        = var.function_name
  project     = var.project_id
  location    = var.region
  description = "Knowledge Factory PDF ingestion pipeline"

  

  ##################################################
  # Build Configuration
  ##################################################

  build_config {

    runtime     = var.runtime
    entry_point = var.entry_point

    source {

      storage_source {
        bucket = var.source_bucket
        object = var.source_object
      }

    }
  }

  ##################################################
  # Runtime Configuration
  ##################################################

  service_config {

    service_account_email = var.service_account_email

    available_memory = var.memory

    timeout_seconds = var.timeout_seconds

    max_instance_count = var.max_instance_count
    min_instance_count = var.min_instance_count

    ingress_settings = var.ingress_settings

    environment_variables = {

      PROJECT_ID = var.project_id

      REGION = var.region

      RAW_BUCKET = var.raw_bucket

      PROCESSED_BUCKET = var.processed_bucket

      FIRESTORE_DATABASE = var.firestore_database

      DOCUMENT_AI_PROCESSOR = var.document_ai_processor

      MAX_CHUNK_PAGES = tostring(var.max_chunk_pages)

    }

  }

  ##################################################
  # Eventarc Trigger
  ##################################################

  event_trigger {

    trigger_region = var.region

    event_type = "google.cloud.storage.object.v1.finalized"

    retry_policy = var.retry_policy

    event_filters {

      attribute = "bucket"
      value     = var.raw_bucket

    }

  }

}