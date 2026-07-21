module "raw-storage" {
  source = "./modules/storage"

  bucket_name = "${var.project_id}-raw"
  location    =  var.region
  storage_class = "STANDARD"
}