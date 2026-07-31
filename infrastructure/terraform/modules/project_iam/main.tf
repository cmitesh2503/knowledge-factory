resource "google_project_iam_member" "member" {

  for_each = var.bindings

  project = var.project_id

  member = "serviceAccount:${each.value.member}"

  role = each.value.role

}

resource "google_project_iam_member" "gcs_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"

  member = "serviceAccount:service-63974849828@gs-project-accounts.iam.gserviceaccount.com"
}