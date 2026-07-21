output "bucket_names"{
    description = "Names os all storage buckets"

    value = {
        for key, bucket in google_storage_bucket.bucket :
        key => bucket.name
    }
}