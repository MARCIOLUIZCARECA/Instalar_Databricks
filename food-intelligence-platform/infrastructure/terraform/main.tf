data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  # dev e prod sempre; hml só quando o workspace existir (workspace_ids.hml).
  has_hml = contains(keys(var.workspace_ids), "hml")

  # Dois buckets, cada um com dev/ hml/ prod/:
  # - raw:       arquivos como chegaram (CSV). Fonte da camada bronze.
  # - lakehouse: tabelas Delta (bronze, silver, gold) dos catálogos food_<env>.
  buckets = {
    raw       = "food-intelligence-raw-${local.aws_account_id}"
    lakehouse = "food-intelligence-lakehouse-${local.aws_account_id}"
  }

  # IAM role que o Unity Catalog assume para ler/gravar nos dois buckets.
  uc_role_name = "food-intelligence-uc-role"
  uc_role_arn  = "arn:aws:iam::${local.aws_account_id}:role/${local.uc_role_name}"

  # Grupos da seção 4 do PRD.
  groups = ["platform-admins", "data-engineering", "marketing-team", "operations-team", "executives"]

  # Quem entra em qual workspace (e com que papel).
  # Matriz da seção 4 do PRD: negócio só enxerga PROD.
  workspace_access = {
    dev = { "platform-admins" = "ADMIN", "data-engineering" = "USER" }
    hml = { "platform-admins" = "ADMIN", "data-engineering" = "USER" }
    prod = {
      "platform-admins"  = "ADMIN"
      "data-engineering" = "USER"
      "marketing-team"   = "USER"
      "operations-team"  = "USER"
      "executives"       = "USER"
    }
  }

  workspace_assignments = merge([
    for env, groups in local.workspace_access : {
      for group, role in groups : "${env}/${group}" => { env = env, group = group, role = role }
    } if contains(keys(var.workspace_ids), env)
  ]...)
}
