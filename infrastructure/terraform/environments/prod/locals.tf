locals {

  storage_iam_bindings = {

    cloudrun_raw_viewer = {

      bucket = module.storage.bucket_names["raw"]

      role = "roles/storage.objectViewer"

      member = module.service_accounts.service_account_emails["cloudrun"]
    }

    cloudrun_processed_creator = {

      bucket = module.storage.bucket_names["processed"]

      role = "roles/storage.objectCreator"

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

  publisher_firestore = {
    member = module.service_accounts.service_account_emails["publisher"]
    role   = "roles/datastore.user"
  }

}

}

