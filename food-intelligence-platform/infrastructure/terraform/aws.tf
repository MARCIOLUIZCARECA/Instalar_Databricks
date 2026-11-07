# Buckets de DADOS do projeto (diferentes do bucket raiz dos workspaces).
#
# s3://food-intelligence-raw-<AWS_ACCOUNT_ID>/        arquivos como chegaram
# ├── dev/orders/   orders.csv, stores.csv
# ├── hml/orders/
# └── prod/orders/
#
# s3://food-intelligence-lakehouse-<AWS_ACCOUNT_ID>/  tabelas Delta (bronze, silver, gold)
# ├── dev/    (catálogo food_dev)
# ├── hml/    (catálogo food_hml)
# └── prod/   (catálogo food_prod)

resource "aws_s3_bucket" "this" {
  for_each = local.buckets

  bucket = each.value

  # Didático: deixa o destroy apagar o bucket com arquivos. Em produção, false.
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Trust policy da role: o Unity Catalog da Databricks pode assumir, desde que
# venha com o External ID da storage credential; a role também assume a si mesma.
# Mesmo padrão do stack de infraestrutura (terraform/aws_iam.tf).
data "databricks_aws_unity_catalog_assume_role_policy" "uc" {
  provider = databricks.dev

  aws_account_id = local.aws_account_id
  role_name      = local.uc_role_name
  external_id    = databricks_storage_credential.food.aws_iam_role[0].external_id
}

resource "aws_iam_role" "uc" {
  name               = local.uc_role_name
  description        = "Unity Catalog: acesso aos buckets raw e lakehouse do Food Intelligence"
  assume_role_policy = data.databricks_aws_unity_catalog_assume_role_policy.uc.json
}

resource "aws_iam_role_policy" "uc_s3" {
  name = "food-intelligence-s3-access"
  role = aws_iam_role.uc.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [for b in aws_s3_bucket.this : "${b.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = [for b in aws_s3_bucket.this : b.arn]
      },
      {
        Effect   = "Allow"
        Action   = ["sts:AssumeRole"]
        Resource = [local.uc_role_arn]
      },
    ]
  })
}

# Espera o IAM propagar antes de a Databricks validar as external locations.
resource "time_sleep" "uc_role" {
  create_duration = "30s"

  triggers = {
    role_arn  = aws_iam_role.uc.arn
    s3_policy = aws_iam_role_policy.uc_s3.id
  }
}
