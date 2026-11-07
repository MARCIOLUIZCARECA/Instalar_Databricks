# Autenticação: NENHUM segredo em arquivo, só NOMES de profiles.
#
# - aws:              profile do AWS CLI (~/.aws/config).
# - databricks.account: profile de CONTA (accounts.cloud.databricks.com).
#                     Cria grupos, usuários e atribui grupos aos workspaces.
# - databricks.dev/hml/prod: um profile por WORKSPACE (databricks auth login
#                     --host <url do workspace> --profile food-dev ...).
#                     Criam os objetos do Unity Catalog.
#
# Por que um provider por workspace? Os catálogos são ISOLADOS (cada um só
# aparece no seu workspace). Um catálogo food_prod criado a partir do FOOD-DEV
# deixaria de ser visível para quem o criou; então cada catálogo é criado pelo
# provider do seu próprio workspace.

provider "aws" {
  profile = var.aws_profile
  region  = var.region

  default_tags {
    tags = var.tags
  }
}

provider "databricks" {
  alias      = "account"
  host       = "https://accounts.cloud.databricks.com"
  account_id = var.databricks_account_id
  profile    = var.databricks_account_profile
}

provider "databricks" {
  alias   = "dev"
  profile = var.workspace_profiles["dev"]
}

# Com 2 ambientes (sem hml), este provider aponta para o profile de dev só para
# o Terraform conseguir inicializar; nenhum recurso o usa (module.hml tem count = 0).
provider "databricks" {
  alias   = "hml"
  profile = contains(keys(var.workspace_ids), "hml") ? var.workspace_profiles["hml"] : var.workspace_profiles["dev"]
}

provider "databricks" {
  alias   = "prod"
  profile = var.workspace_profiles["prod"]
}
