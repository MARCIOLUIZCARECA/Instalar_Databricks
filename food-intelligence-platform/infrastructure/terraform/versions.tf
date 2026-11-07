# Stack de GOVERNANÇA do Food Intelligence Platform.
# Roda DEPOIS do stack de infraestrutura (../../../terraform), que cria os
# workspaces FOOD-DEV, FOOD-HML e FOOD-PROD.
#
# Mesmas versões do stack de infraestrutura (testadas juntas).

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "1.141.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.14"
    }
  }
}
