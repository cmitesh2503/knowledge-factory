locals {

  iam_bindings = {

    cloudrun_storage_viewer = {

      member = module.service_accounts.service_account_emails["cloudrun"]
      role   = "roles/storage.objectViewer"
    }

    cloudrun_storage_creator = {

      member = module.service_accounts.service_account_emails["cloudrun"]
      role   = "roles/storage.objectCreator"
    }

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
