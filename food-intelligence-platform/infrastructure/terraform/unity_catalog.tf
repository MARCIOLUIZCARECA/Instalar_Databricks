# Unity Catalog: a ponte entre o S3 (dado físico) e as tabelas (metadado).
#
#   IAM role ──> storage credential ──┬─> external location food-raw-<env>
#                                     │      └── volume food_<env>.orders.raw   (CSV como chegou)
#                                     └─> external location food-lakehouse-<env>
#                                            └── catálogo food_<env>            (tabelas Delta)

# Storage credential: o Unity Catalog guarda QUAL role assumir.
# Criada antes da role existir (o ARN é montado pelo nome); a role usa o
# External ID gerado aqui na trust policy (aws.tf).
resource "databricks_storage_credential" "food" {
  provider = databricks.dev

  name    = "food-intelligence-s3"
  comment = "Acesso aos buckets raw e lakehouse do Food Intelligence (Terraform)"
  owner   = databricks_group.this["platform-admins"].display_name

  aws_iam_role {
    role_arn = local.uc_role_arn
  }

  # A role ainda não existe neste momento; a validação acontece nas external locations.
  skip_validation = true
}

# Um bloco por ambiente. Cada um usa o provider do SEU workspace.
module "dev" {
  source    = "./modules/environment"
  providers = { databricks = databricks.dev }

  env                = "dev"
  workspace_id       = var.workspace_ids["dev"]
  raw_bucket         = aws_s3_bucket.this["raw"].bucket
  lakehouse_bucket   = aws_s3_bucket.this["lakehouse"].bucket
  storage_credential = databricks_storage_credential.food.name
  owner_group        = databricks_group.this["platform-admins"].display_name
  role_ready         = time_sleep.uc_role.id

  # DEV: engenharia desenvolve (lê e escreve).
  catalog_grants = {
    "data-engineering" = ["USE_CATALOG", "USE_SCHEMA", "CREATE_SCHEMA", "CREATE_TABLE", "CREATE_VOLUME", "SELECT", "MODIFY", "READ_VOLUME", "WRITE_VOLUME"]
  }
  schema_grants = {}

  depends_on = [databricks_mws_permission_assignment.this]
}

# HML é opcional: só existe se workspace_ids tiver a chave hml.
module "hml" {
  source    = "./modules/environment"
  providers = { databricks = databricks.hml }
  count     = local.has_hml ? 1 : 0

  env                = "hml"
  workspace_id       = var.workspace_ids["hml"]
  raw_bucket         = aws_s3_bucket.this["raw"].bucket
  lakehouse_bucket   = aws_s3_bucket.this["lakehouse"].bucket
  storage_credential = databricks_storage_credential.food.name
  owner_group        = databricks_group.this["platform-admins"].display_name
  role_ready         = time_sleep.uc_role.id

  # HML: engenharia valida (só leitura); quem escreve é o job publicado.
  catalog_grants = {
    "data-engineering" = ["USE_CATALOG", "USE_SCHEMA", "SELECT", "READ_VOLUME"]
  }
  schema_grants = {}

  depends_on = [databricks_mws_permission_assignment.this]
}

module "prod" {
  source    = "./modules/environment"
  providers = { databricks = databricks.prod }

  env                = "prod"
  workspace_id       = var.workspace_ids["prod"]
  raw_bucket         = aws_s3_bucket.this["raw"].bucket
  lakehouse_bucket   = aws_s3_bucket.this["lakehouse"].bucket
  storage_credential = databricks_storage_credential.food.name
  owner_group        = databricks_group.this["platform-admins"].display_name
  role_ready         = time_sleep.uc_role.id

  # PROD: engenharia com acesso controlado (leitura).
  # Negócio só entra no catálogo e no schema; o SELECT é dado na tabela Gold
  # pelo próprio pipeline (notebooks/04_gold.py), porque a tabela nasce lá.
  catalog_grants = {
    "data-engineering" = ["USE_CATALOG", "USE_SCHEMA", "SELECT", "READ_VOLUME"]
    "marketing-team"   = ["USE_CATALOG"]
    "operations-team"  = ["USE_CATALOG"]
    "executives"       = ["USE_CATALOG"]
  }
  schema_grants = {
    "marketing-team"  = ["USE_SCHEMA"]
    "operations-team" = ["USE_SCHEMA"]
    "executives"      = ["USE_SCHEMA"]
  }

  depends_on = [databricks_mws_permission_assignment.this]
}
