# Autenticação: NENHUM segredo fica em arquivo.
# - AWS: usa um profile do AWS CLI (~/.aws/config), por exemplo via `aws sso login`.
# - Databricks: usa um profile de CONTA do ~/.databrickscfg, criado com
#   `databricks auth login --host https://accounts.cloud.databricks.com --account-id <ID>`.

provider "aws" {
  profile = var.aws_profile
  region  = var.region

  # Todas as peças criadas na AWS recebem estas tags (facilita achar e limpar depois).
  default_tags {
    tags = var.tags
  }
}

# Provider no nível de CONTA (Account Console), não de workspace.
# É ele que registra credential, storage configuration e cria o workspace.
provider "databricks" {
  alias      = "mws"
  host       = "https://accounts.cloud.databricks.com"
  account_id = var.databricks_account_id
  profile    = var.databricks_account_profile
}
