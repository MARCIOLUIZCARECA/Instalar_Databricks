# Arquitetura

A explicação detalhada de **control plane × compute plane**, External ID e custos de um workspace clássico está no manual: [`../../manual/arquitetura/README.md`](../../manual/arquitetura/README.md) e [`../../manual/fundamentos.md`](../../manual/fundamentos.md). Aqui está o que o Food Intelligence monta em cima disso.

## Visão geral

```text
                         Databricks Account (accounts.cloud.databricks.com)
                         ├── grupos e usuários (uma vez só, na conta)
                         ├── metastore Unity Catalog (us-east-2)
                         └── workspaces
                              ├── FOOD-DEV   ── catálogo food_dev   (isolado)
                              └── FOOD-PROD  ── catálogo food_prod  (isolado)
                                  (FOOD-HML + food_hml: opcional)
                                                   └── orders
                                                        ├── raw  (volume → S3 raw)
                                                        ├── bronze_orders, bronze_stores
                                                        ├── silver_orders, silver_stores
                                                        └── gold_sales_by_store ──► Dashboard · App · Genie

Conta AWS (928844615034, us-east-2)
├── databricks-food-root-<conta>           bucket raiz dos workspaces (cada um no seu prefixo)
├── food-intelligence-raw-<conta>          arquivos brutos     dev/ prod/  orders/*.csv
├── food-intelligence-lakehouse-<conta>    tabelas Delta       dev/ prod/
├── databricks-food-cross-account-role     compute (EC2, VPC) dos workspaces
├── databricks-food-storage-role           UC do bucket raiz
├── food-intelligence-uc-role              UC dos buckets raw e lakehouse
└── 2 × Databricks-managed VPC (uma por workspace, cada uma com NAT Gateway)
```

## Dois stacks de Terraform

| Stack | Pasta | Nível | Cria |
|---|---|---|---|
| Infraestrutura | [`../../terraform`](../../terraform) | Conta Databricks + AWS | bucket raiz, roles, credential, storage configuration, **workspaces DEV e PROD** |
| Governança | [`../infrastructure/terraform`](../infrastructure/terraform) | Conta + cada workspace | buckets raw/lakehouse, role do UC, storage credential, external locations, catálogos, schema, volume, **grupos, usuários, atribuições e grants** |

Separados de propósito: o primeiro é o "prédio" (raramente muda); o segundo é a "portaria" (muda sempre que entra gente ou dado novo).

## Metadado × dado físico

| Você vê (Unity Catalog) | Onde o dado está (S3) |
|---|---|
| `/Volumes/food_dev/orders/raw/orders.csv` | `s3://food-intelligence-raw-<conta>/dev/orders/orders.csv` |
| `food_dev.orders.bronze_orders` | `s3://food-intelligence-lakehouse-<conta>/dev/__unitystorage/...` |

Ninguém recebe chave da AWS. O Unity Catalog assume a role `food-intelligence-uc-role` e decide, por grant, quem pode ler o quê.

## Camadas

| Camada | Tabela | Regra |
|---|---|---|
| Raw | arquivos no bucket raw | como chegou; nunca é alterado |
| Bronze | `bronze_orders`, `bronze_stores` | cópia fiel em Delta (tudo texto) + `_source_file`, `_ingested_at` |
| Silver | `silver_orders`, `silver_stores` | sem duplicados, tipos corretos, nulos tratados, status padronizado |
| Gold | `gold_sales_by_store` | loja × dia, só pedidos entregues: pedidos, faturamento, ticket médio |

## Compute

| Uso | Compute |
|---|---|
| Notebooks interativos e job da pipeline | Serverless |
| Dashboard, App e Genie | SQL warehouse clássico `Food Classic Warehouse` (o serverless deu 403 nos buckets da conta do ensaio; ver [troubleshooting.md](troubleshooting.md)) |
| Clusters clássicos (opcional) | EC2 na VPC do workspace |
