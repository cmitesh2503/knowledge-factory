output "bucket_iam_bindings" {
  value = {

    for key, value in google_storage_bucket_iam_member.member :

    key => value.id
  }
}