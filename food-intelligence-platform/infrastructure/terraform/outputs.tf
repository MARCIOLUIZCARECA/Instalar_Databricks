output "buckets" {
  description = "Buckets do projeto: raw (arquivos) e lakehouse (tabelas)."
  value       = { for k, b in aws_s3_bucket.this : k => b.bucket }
}

output "catalogs" {
  description = "Catálogos por ambiente."
  value       = merge({ dev = module.dev.catalog, prod = module.prod.catalog }, local.has_hml ? { hml = module.hml[0].catalog } : {})
}

output "raw_volume_paths" {
  description = "Onde a camada bronze lê os arquivos (volume do Unity Catalog)."
  value       = merge({ dev = module.dev.raw_volume_path, prod = module.prod.raw_volume_path }, local.has_hml ? { hml = module.hml[0].raw_volume_path } : {})
}

output "raw_s3_paths" {
  description = "Para onde o data/upload_to_s3.sh envia os CSVs."
  value       = merge({ dev = module.dev.raw_s3_path, prod = module.prod.raw_s3_path }, local.has_hml ? { hml = module.hml[0].raw_s3_path } : {})
}
