locals {

  storage_iam_bindings = {

    cloudrun_raw_viewer = {

      bucket = module.storage.bucket_names["raw"]

      role = "roles/storage.objectViewer"

      member = module.service_accounts.service_account_emails["cloudrun"]
    }

    cloudrun_processed_object_admin = {

      bucket = module.storage.bucket_names["processed"]

      role = "roles/storage.objectAdmin"

      member = module.service_accounts.service_account_emails["cloudrun"]
    }
  }

  project_iam_bindings = {

    cloudrun_firestore = {

      member = module.service_accounts.service_account_emails["cloudrun"]
      role   = "roles/datastore.user"
    }

    cloudrun_secretmanager = {

      member = module.service_accounts.service_account_emails["cloudrun"]
      role   = "roles/secretmanager.secretAccessor"
    }

    cloudrun_documentai = {

      member = module.service_accounts.service_account_emails["cloudrun"]
      role   = "roles/documentai.apiUser"
    }

    workflow_storage = {
      member = module.service_accounts.service_account_emails["workflow"]
      role   = "roles/storage.objectViewer"

    }

    workflow_logging = {
      member = module.service_accounts.service_account_emails["workflow"]
      role   = "roles/logging.logWriter"
    }

    publisher_firestore = {
      member = module.service_accounts.service_account_emails["publisher"]
      role   = "roles/datastore.user"
    }



  }

  firestore = {
    database_name = "(default)"

    location_id = "asia-south1"

    database_type = "FIRESTORE_NATIVE"
  }

  workflow = {

    name = "Knowledge-factory-pipeline"

    region = "asia-south1"

    labels = {

      application = "knowledge-factory"

      environment = "prod"

      managed-by = "terraform"
    }
  }

  document_ai = {
    display_name = "knowledge-factory-layout-parser"

    location = "us"

    processor_type = "LAYOUT_PARSER_PROCESSOR"
  }
}

