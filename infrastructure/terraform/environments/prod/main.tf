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