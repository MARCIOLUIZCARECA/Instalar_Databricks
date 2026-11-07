variable "databricks_account_id" {
  description = "Databricks Account ID (Account Console > menu do usuário). Também é o External ID das trust policies."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.databricks_account_id))
    error_message = "O Databricks Account ID é um UUID, no formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."
  }
}

variable "aws_profile" {
  description = "Profile do AWS CLI usado pelo Terraform (~/.aws/config)."
  type        = string
  default     = "agent-toolkit"
}

variable "databricks_account_profile" {
  description = "Profile de CONTA do ~/.databrickscfg (criado com `databricks auth login` no host accounts.cloud.databricks.com)."
  type        = string
  default     = "workshop-account"
}

variable "prefix" {
  description = "Prefixo dos nomes. Com o default, os nomes ficam iguais aos do manual (databricks-workshop-...)."
  type        = string
  default     = "workshop"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.prefix))
    error_message = "Use de 3 a 20 caracteres: letras minúsculas, números e hífen (o prefixo entra no nome do bucket S3)."
  }
}

variable "environments" {
  description = "Workspaces a criar: chave do ambiente => nome do workspace. Default: DEV e PROD. Para 3 ambientes, inclua hml = \"FOOD-HML\"; para estudar, deixe só dev."
  type        = map(string)
  default = {
    dev  = "FOOD-DEV"
    prod = "FOOD-PROD"
  }

  validation {
    condition     = length(var.environments) > 0
    error_message = "Informe pelo menos um ambiente."
  }
}

variable "region" {
  description = "Região AWS do bucket e do workspace (precisam ser a mesma). Manual: Ohio."
  type        = string
  default     = "us-east-2"
}

variable "enable_file_events" {
  description = "Passo 4.5 (opcional): adiciona à storage role a policy de file events (SQS/SNS para o Auto Loader)."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags aplicadas a todos os recursos da AWS."
  type        = map(string)
  default = {
    Projeto       = "setup-databricks-profissional"
    Evento        = "workshop-jornada-de-dados"
    GerenciadoPor = "terraform"
  }
}
