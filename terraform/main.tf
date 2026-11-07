# Valores compartilhados por todos os arquivos.
# Os nomes seguem a tabela "Anote estes valores" do manual (seção 0).

# Descobre o AWS Account ID da conta logada (o "AWS_ACCOUNT_ID" do manual),
# sem precisar digitar.
data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id

  # Conta AWS da Databricks (control plane). É a mesma para todos os clientes.
  databricks_aws_account_id = "414351767826"

  # Passo 2: nome único no mundo, terminando com o AWS Account ID.
  root_bucket_name = "databricks-${var.prefix}-root-${local.aws_account_id}"

  # Passo 4: storage role do Unity Catalog.
  storage_role_name = "databricks-${var.prefix}-storage-role"
  # ARN montado a partir do NOME (e não de aws_iam_role.storage.arn).
  # Assim a role pode citar a si mesma sem criar um ciclo no Terraform.
  storage_role_arn = "arn:aws:iam::${local.aws_account_id}:role/${local.storage_role_name}"

  # Passo 5: cross-account role (compute).
  cross_account_role_name = "databricks-${var.prefix}-cross-account-role"

  # Passo 6: objetos do Account Console.
  credentials_name           = "databricks-${var.prefix}-credential"
  storage_configuration_name = "databricks-${var.prefix}-storage"

  # Um workspace por ambiente (FOOD-DEV e FOOD-PROD; FOOD-HML opcional), todos usando
  # a mesma credential e a mesma storage configuration.
  workspace_names = var.environments
}
