# AWS

O passo a passo com prints (bucket raiz, bucket policy, storage role, cross-account role) está no manual: [`../../manual/README.md`](../../manual/README.md), seções 2 a 5. O Terraform [`../../terraform`](../../terraform) faz o mesmo por código.

## O que o Food Intelligence acrescenta

Criado pelo stack de governança ([`../infrastructure/terraform/aws.tf`](../infrastructure/terraform/aws.tf)):

| Recurso | Nome | Para quê |
|---|---|---|
| Bucket | `food-intelligence-raw-<AWS_ACCOUNT_ID>` | Arquivos brutos por ambiente (`dev/orders/`, `prod/orders/`) |
| Bucket | `food-intelligence-lakehouse-<AWS_ACCOUNT_ID>` | Tabelas Delta dos catálogos (`dev/`, `prod/`) |
| IAM role | `food-intelligence-uc-role` | Assumida pelo Unity Catalog para ler/gravar nos dois buckets |

Os dois buckets: privados, SSE-S3, *Object Ownership* = bucket owner.

A role usa o mesmo padrão *self-assuming* da storage role do manual (passo 4.4), com o External ID gerado pela storage credential `food-intelligence-s3`.

## Por que dois buckets?

- **raw** recebe arquivos de sistemas de origem. Pode ter regras próprias (retenção longa, acesso de quem envia os arquivos).
- **lakehouse** é do Databricks. Ninguém escreve nele por fora do Unity Catalog.

Separar deixa claro, na aula, a diferença entre "o arquivo que chegou" e "a tabela que a plataforma gerencia".

## Enviar os dados

```bash
python data/generate_orders.py                      # gera data/output/orders.csv e stores.csv
./data/upload_to_s3.sh dev  <profile-aws>
./data/upload_to_s3.sh prod <profile-aws>
```
