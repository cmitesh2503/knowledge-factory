output "workflow_name" {

  description = "Workflow name"

  value = google_workflows_workflow.pipeline.name

}

output "workflow_id" {

  description = "Workflow ID"

  value = google_workflows_workflow.pipeline.id

}