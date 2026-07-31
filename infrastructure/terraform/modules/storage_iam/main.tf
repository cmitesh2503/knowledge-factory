resource "google_storage_bucket_iam_member" "member" {

  for_each = var.bindings

  bucket = each.value.bucket

  role = each.value.role

  member = "serviceAccount:${each.value.member}"

}

resource "google_storage_bucket_iam_member" "eventarc_raw_bucket_viewer" {
  bucket = var.raw_bucket_name
  role   = "roles/storage.legacyBucketReader"

  member = "serviceAccount:service-63974849828@gcp-sa-eventarc.iam.gserviceaccount.com"
}