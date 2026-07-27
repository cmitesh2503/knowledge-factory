resource "google_storage_bucket_iam_member" "member" {

  for_each = var.bindings

  bucket = each.value.bucket

  role = each.value.role

  member = "serviceAccount:${each.value.member}"

}