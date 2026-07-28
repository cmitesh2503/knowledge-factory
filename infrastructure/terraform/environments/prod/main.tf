module "storage" {
  source = "../../modules/storage"

  location = var.region

  buckets = {
    raw = {
      name          = "${var.project_id}-raw"
      storage_class = "STANDARD"
    }

    processed = {
      name          = "${var.project_id}-processed"
      storage_class = "STANDARD"
    }

    published = {
      name          = "${var.project_id}-published"
      storage_class = "STANDARD"
    }

    archive = {
      name          = "${var.project_id}-archive"
      storage_class = "COLDLINE"
    }
  }
}

module "service_accounts" {
  source = "../../modules/service_accounts"
  service_accounts = {
    cloudrun = {

      account_id = "knowledge-factory-cloudrun"

      display_name = "Knowledge Factory Cloud Run"

      description = "Runs the backend application"

    }

    workflow = {
      account_id = "knowledge-factory-workflow"

      display_name = "Knowledge Factory Workflow"

      description = "Execution ingestion workflows"

    }

    publisher = {
      account_id = "knowledge-factory-publisher"

      display_name = "Knowledge Factory Publisher"

      description = "Publishes Curriculum"

    }

    scheduler = {
      account_id = "knowledge-factory-scheduler"

      display_name = "Knowledge Factory Scheduler"

      description = " Runs scheduled jobs"
    }

  }

}

module "project_iam" {
  source = "../../modules/project_iam"

  project_id = var.project_id

  bindings = local.project_iam_bindings
}

module "storage_iam" {
  source = "../../modules/storage_iam"

  bindings = local.storage_iam_bindings
}

module "firestore" {

  source = "../../modules/firestore"

  project_id = var.project_id

  location_id = local.firestore.location_id

  database_name = local.firestore.database_name

  database_type = local.firestore.database_type
}

module "workflows" {
  source = "../../modules/workflows"

  project_id = var.project_id

  region = local.workflow.region

  workflow_name = local.workflow.name

  service_account_email = module.service_accounts.service_account_emails["workflow"]

  labels = local.workflow.labels
}
