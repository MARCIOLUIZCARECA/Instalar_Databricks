# Identidades no nível de CONTA: grupos, usuários e quem entra em qual workspace.
# Um usuário é cadastrado UMA vez na conta e atribuído aos workspaces pelos grupos.

resource "databricks_group" "this" {
  provider = databricks.account
  for_each = toset(local.groups)

  display_name = each.value
}

# Administradores da plataforma (pessoas reais, ex.: o instrutor).
data "databricks_user" "admins" {
  provider = databricks.account
  for_each = toset(var.platform_admins)

  user_name = each.value
}

resource "databricks_group_member" "admins" {
  provider = databricks.account
  for_each = data.databricks_user.admins

  group_id  = databricks_group.this["platform-admins"].id
  member_id = each.value.id
}

# Usuários fictícios da demonstração (Admin, Engenheiro, Analistas, Diretor).
resource "databricks_user" "demo" {
  provider = databricks.account
  for_each = var.demo_users

  user_name = each.key
}

resource "databricks_group_member" "demo" {
  provider = databricks.account
  for_each = var.demo_users

  group_id  = databricks_group.this[each.value].id
  member_id = databricks_user.demo[each.key].id
}

# Atribuição dos GRUPOS aos workspaces (não de pessoas uma a uma).
# É aqui que o marketing-team "não existe" em DEV e HML.
resource "databricks_mws_permission_assignment" "this" {
  provider = databricks.account
  for_each = local.workspace_assignments

  workspace_id = var.workspace_ids[each.value.env]
  principal_id = databricks_group.this[each.value.group].id
  permissions  = [each.value.role]
}
