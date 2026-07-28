resource "google_workflows_workflow" "pipeline" {

  project = var.project_id

  region = var.region

  name = var.workflow_name

  service_account = var.service_account_email

  labels = var.labels

  source_contents = templatefile(
    "${path.module}/templates/knowledge-factory-pipeline.yaml",
    {}
  )

}