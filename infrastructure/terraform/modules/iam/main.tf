resource "google_project_iam_member" "member" {

    for_each = var.bindings

    project = var.project_id

    member = "serviceAccount:${each.value.member}"

    role   = each.value.role

}