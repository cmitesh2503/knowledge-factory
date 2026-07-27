output "service_account_emails" {

  description = "Email address of the created service accounts."

  value = { for key, sa in google_service_account.service_account :

  key => sa.email }
}