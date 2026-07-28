output "database_name" {

  description = " Firetore database name"

  value = google_firestore_database.database.name
}

output "database_id" {

  description = " Firestore database id"

  value = google_firestore_database.database.id
}

output "database_type" {
  description = "Firestore database type"

  value = google_firestore_database.database.type
}

output "location_id" {
  description = "Firestore database location"

  value = google_firestore_database.database.location_id
}