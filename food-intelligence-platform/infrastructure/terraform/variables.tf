variable "databricks_account_id" {
  description = "Databricks Account ID (Account Console > menu do usuário)."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.databricks_account_id))
    error_message = "O Databricks Account ID é um UUID, no formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."
  }
}

variable "aws_profile" {
  description = "Profile do AWS CLI (a mesma conta AWS dos workspaces)."
  type        = string
}

variable "databricks_account_profile" {
  description = "Profile de CONTA do ~/.databrickscfg."
  type        = string
  default     = "workshop-account"
}

variable "workspace_profiles" {
  description = "Profile do ~/.databrickscfg de cada workspace (criados com databricks auth login --host <url>)."
  type        = map(string)
  default = {
    dev  = "food-dev"
    hml  = "food-hml" # só é usado se workspace_ids tiver hml
    prod = "food-prod"
  }
}

variable "workspace_ids" {
  description = "ID numérico de cada workspace: copie o output workspace_ids do stack ../../../terraform. dev e prod são obrigatórios; hml é opcional."
  type        = map(number)

  validation {
    condition     = alltrue([for env in ["dev", "prod"] : contains(keys(var.workspace_ids), env)]) && alltrue([for env in keys(var.workspace_ids) : contains(["dev", "hml", "prod"], env)])
    error_message = "Informe os IDs de dev e prod (hml é opcional). Chaves aceitas: dev, hml, prod."
  }
}

variable "region" {
  description = "Região AWS (a mesma dos workspaces e do metastore)."
  type        = string
  default     = "us-east-2"
}

variable "platform_admins" {
  description = "E-mails que entram no grupo platform-admins (inclua o seu, para administrar os catálogos)."
  type        = list(string)
}

variable "demo_users" {
  description = <<-EOT
    Usuários fictícios da demonstração: e-mail => grupo.
    Dica: use plus-addressing do seu e-mail (voce+marketing@empresa.com) para
    conseguir logar com cada perfil e testar as permissões.
  EOT
  type        = map(string)
  default     = {}

  validation {
    condition = alltrue([for g in values(var.demo_users) : contains(
      ["platform-admins", "data-engineering", "marketing-team", "operations-team", "executives"], g
    )])
    error_message = "Grupo inválido. Use: platform-admins, data-engineering, marketing-team, operations-team ou executives."
  }
}

variable "tags" {
  description = "Tags aplicadas a todos os recursos da AWS."
  type        = map(string)
  default = {
    Projeto       = "food-intelligence-platform"
    Evento        = "workshop-jornada-de-dados"
    GerenciadoPor = "terraform"
  }
}
