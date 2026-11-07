# Um ambiente (dev, hml ou prod) no Unity Catalog:
#   external location raw       s3://food-intelligence-raw-<conta>/<env>/        -> volume food_<env>.orders.raw
#   external location lakehouse s3://food-intelligence-lakehouse-<conta>/<env>/  -> catálogo food_<env> (tabelas)
# + schema orders + grants. O catálogo é isolado no workspace do ambiente.

terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

variable "env" { type = string }
variable "workspace_id" { type = number }
variable "raw_bucket" { type = string }
variable "lakehouse_bucket" { type = string }
variable "storage_credential" { type = string }
variable "owner_group" { type = string }
variable "role_ready" {
  description = "Só para ordenar: a external location espera a role IAM propagar."
  type        = string
}
variable "catalog_grants" { type = map(list(string)) }
variable "schema_grants" { type = map(list(string)) }

locals {
  raw_prefix       = "s3://${var.raw_bucket}/${var.env}"
  lakehouse_prefix = "s3://${var.lakehouse_bucket}/${var.env}"
}

# A Databricks testa leitura/escrita nas duas URLs ao criar.
resource "databricks_external_location" "raw" {
  name            = "food-raw-${var.env}"
  url             = "${local.raw_prefix}/"
  credential_name = var.storage_credential
  owner           = var.owner_group
  comment         = "Arquivos brutos de ${upper(var.env)} (role pronta: ${var.role_ready})"
}

resource "databricks_external_location" "lakehouse" {
  name            = "food-lakehouse-${var.env}"
  url             = "${local.lakehouse_prefix}/"
  credential_name = var.storage_credential
  owner           = var.owner_group
  comment         = "Tabelas Delta de ${upper(var.env)} (role pronta: ${var.role_ready})"
}

# Catálogo food_<env>. As tabelas gerenciadas (bronze, silver, gold) ficam no bucket lakehouse.
# ISOLATED: o catálogo só aparece nos workspaces vinculados (binding abaixo).
resource "databricks_catalog" "this" {
  name           = "food_${var.env}"
  comment        = "Food Intelligence · ${upper(var.env)}"
  storage_root   = "${local.lakehouse_prefix}/"
  isolation_mode = "ISOLATED"
  owner          = var.owner_group

  depends_on = [databricks_external_location.lakehouse]
}

resource "databricks_workspace_binding" "this" {
  securable_name = databricks_catalog.this.name
  securable_type = "catalog"
  workspace_id   = var.workspace_id
  binding_type   = "BINDING_TYPE_READ_WRITE"
}

resource "databricks_schema" "orders" {
  catalog_name = databricks_catalog.this.name
  name         = "orders"
  comment      = "Pedidos: bronze, silver e gold"
  owner        = var.owner_group
}

# Volume externo apontando para o bucket RAW:
# /Volumes/food_<env>/orders/raw  ==  s3://food-intelligence-raw-<conta>/<env>/orders/
resource "databricks_volume" "raw" {
  catalog_name     = databricks_catalog.this.name
  schema_name      = databricks_schema.orders.name
  name             = "raw"
  volume_type      = "EXTERNAL"
  storage_location = "${local.raw_prefix}/orders"
  owner            = var.owner_group
  comment          = "Arquivos brutos (orders.csv, stores.csv): fonte da camada bronze"

  depends_on = [databricks_external_location.raw]
}

# databricks_grant (singular) não é autoritativo: não apaga grants feitos por
# outros (ex.: o service principal do App, criado pelo bundle).
resource "databricks_grant" "catalog" {
  for_each = var.catalog_grants

  catalog    = databricks_catalog.this.name
  principal  = each.key
  privileges = each.value
}

resource "databricks_grant" "schema" {
  for_each = var.schema_grants

  schema     = "${databricks_catalog.this.name}.${databricks_schema.orders.name}"
  principal  = each.key
  privileges = each.value
}

output "catalog" { value = databricks_catalog.this.name }
output "raw_volume_path" { value = "/Volumes/${databricks_catalog.this.name}/${databricks_schema.orders.name}/${databricks_volume.raw.name}" }
output "raw_s3_path" { value = "${local.raw_prefix}/orders/" }
