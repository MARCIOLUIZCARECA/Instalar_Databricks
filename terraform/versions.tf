# Versões do Terraform e dos providers.
# Fixamos as versões para que os ~200 alunos rodem exatamente o mesmo código
# que foi testado no ensaio (06/11/2026).

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    # AWS: bucket S3 e IAM roles (passos 2 a 5 do manual).
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    # Databricks: credential, storage configuration e workspace (Account Console).
    databricks = {
      source  = "databricks/databricks"
      version = "1.141.0"
    }

    # time: pausas (time_sleep) para o IAM da AWS propagar antes da validação da Databricks.
    time = {
      source  = "hashicorp/time"
      version = "~> 0.14"
    }
  }
}
