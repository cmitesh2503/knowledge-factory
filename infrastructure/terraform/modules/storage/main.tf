resource "google_storage_bucket" "bucket" {

  for_each = var.buckets

  name          = each.value.name
  location      = var.location
  storage_class = each.value.storage_class

  uniform_bucket_level_access = true



  versioning {
    enabled = true
  }
}