resource "google_storage_bucket" "bucket" {

  for_each = var.buckets

  name          = "${var.project_id}-${each.key}"
  location      = var.location
  storage_class = each.value.storage_class

  uniform_bucket_level_access = true

  force_destroy = false

  versioning {
    enabled = true
  }
}