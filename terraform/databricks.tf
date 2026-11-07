# Account Console da Databricks (passo 6 do manual): registrar as peças da AWS
# e montar o workspace. Tudo aqui usa o provider de CONTA (databricks.mws).

# Credential configuration (bloco "Compute credentials"): aponta para a ③ cross-account role.
# O role_arn vem do time_sleep, então este recurso só é criado 20 s depois da role.
resource "databricks_mws_credentials" "this" {
  provider = databricks.mws

  credentials_name = local.credentials_name
  role_arn         = time_sleep.cross_account_role.triggers["role_arn"]
}

# Storage configuration (bloco "Workspace storage"): ① bucket raiz + ② storage role.
# O campo role_arn é o "IAM role" da tela de storage manual (suportado no provider 1.141.0).
resource "databricks_mws_storage_configurations" "this" {
  provider = databricks.mws

  account_id                 = var.databricks_account_id
  storage_configuration_name = local.storage_configuration_name
  bucket_name                = aws_s3_bucket_policy.root.bucket # depende do bucket JÁ com a policy
  role_arn                   = time_sleep.storage_role.triggers["role_arn"]
}

# Os workspaces clássicos (um por ambiente): juntam credential + storage + rede.
# for_each cria FOOD-DEV e FOOD-PROD (e FOOD-HML, se pedido) reaproveitando a MESMA credential
# e a MESMA storage configuration. Cada workspace grava no bucket raiz sob um
# prefixo próprio (o ID do workspace), então eles não se misturam.
# Cada workspace tem a SUA Databricks-managed VPC (e o seu NAT Gateway).
# - Sem network_id  => Databricks-managed VPC (a Databricks cria VPC, subnets e
#   NAT Gateway na sua conta usando a cross-account role).
# - Sem deployment_name => a URL é gerada automaticamente (dbc-xxxx.cloud.databricks.com).
# - Sem private_access_settings_id => sem PrivateLink ("None" no formulário).
# - O metastore do Unity Catalog da região é atribuído automaticamente.
resource "databricks_mws_workspaces" "this" {
  provider = databricks.mws
  for_each = local.workspace_names

  account_id     = var.databricks_account_id
  workspace_name = each.value
  aws_region     = var.region

  credentials_id           = databricks_mws_credentials.this.credentials_id
  storage_configuration_id = databricks_mws_storage_configurations.this.storage_configuration_id

  # Criar o workspace (e a rede) leva alguns minutos.
  timeouts {
    create = "30m"
  }
}
