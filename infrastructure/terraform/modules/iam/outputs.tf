output "iam_roles" {

    value = {
        for key, value in google_project_iam_member.member :
        key => value.role
    }
}