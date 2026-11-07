# ① Bucket S3 raiz do workspace (passos 2 e 3 do manual).

# Passo 2: o bucket. Guarda logs, resultados de notebooks, DBFS root e,
# sob o prefixo unity-catalog/, os dados do catálogo do workspace.
resource "aws_s3_bucket" "root" {
  bucket = local.root_bucket_name

  # Permite que o `terraform destroy` apague o bucket mesmo com os arquivos que
  # o workspace gravou nele. Didático para o workshop; em produção, use false.
  force_destroy = true

  # Versionamento: não declaramos aws_s3_bucket_versioning, então o bucket nasce
  # sem versionamento (igual ao manual: "Bucket Versioning: Disable").
}

# Passo 2, item 4: Object Ownership = ACLs disabled.
resource "aws_s3_bucket_ownership_controls" "root" {
  bucket = aws_s3_bucket.root.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Passo 2, item 5: Block all public access (os 4 checkboxes marcados).
resource "aws_s3_bucket_public_access_block" "root" {
  bucket = aws_s3_bucket.root.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Passo 2, item 7: Default encryption = SSE-S3 (AES256).
resource "aws_s3_bucket_server_side_encryption_configuration" "root" {
  bucket = aws_s3_bucket.root.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Passo 3: bucket policy. Conteúdo idêntico a manual/policies/03-bucket-policy.json.
#
# Por que não usamos o data source databricks_aws_bucket_policy?
# Na versão 1.141.0 ele gera só o Allow; falta o Deny em unity-catalog/*
# que a documentação atual (e o manual) exige. Por isso escrevemos o JSON aqui.
resource "aws_s3_bucket_policy" "root" {
  bucket = aws_s3_bucket.root.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allow: a conta da Databricks lê/grava o bucket, mas só quando a chamada
        # vem marcada com o SEU Databricks Account ID.
        Sid    = "Grant Databricks Access"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.databricks_aws_account_id}:root"
        }
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation",
        ]
        Resource = [
          "${aws_s3_bucket.root.arn}/*",
          aws_s3_bucket.root.arn,
        ]
        Condition = {
          StringEquals = {
            "aws:PrincipalTag/DatabricksAccountId" = [var.databricks_account_id]
          }
        }
      },
      {
        # Deny: o caminho antigo (DBFS) não acessa a pasta do Unity Catalog.
        Sid    = "Prevent DBFS from accessing Unity Catalog metastore"
        Effect = "Deny"
        Principal = {
          AWS = "arn:aws:iam::${local.databricks_aws_account_id}:root"
        }
        Action   = ["s3:*"]
        Resource = ["${aws_s3_bucket.root.arn}/unity-catalog/*"]
      },
    ]
  })

  # A AWS recusa a policy se o Block Public Access ainda estiver sendo aplicado
  # em paralelo; esperamos ele terminar.
  depends_on = [aws_s3_bucket_public_access_block.root]
}
