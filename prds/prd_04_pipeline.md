# PRD 04 · Pipeline Raw → Bronze → Silver → Gold (em DEV)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md`.

**Pré-requisito:** catálogo `food_dev` e CSVs no volume `food_dev.orders.raw` (PRDs 02 e 03).

**Mensagem da aula:** *"do arquivo bruto ao dado de negócio, e as tabelas são arquivos no seu bucket"*.

---

## 1. Objetivo

Uma única pipeline, simples, que mostra o ciclo de vida do dado. O código nasce **só em DEV**; a promoção é o PRD 05.

Fora de escopo: streaming, Auto Loader com file events, ML, múltiplas pipelines.

## 2. O que construir

O catálogo **não é fixo no código**: vem por parâmetro (`catalog`, padrão `food_dev`), para o mesmo código rodar em PROD.

| Notebook | Faz | Tabela |
|---|---|---|
| `notebooks/01_ingestion.py` | Lê os CSVs do volume `raw` como texto; mostra schema e amostras | — |
| `notebooks/02_bronze.py` | Grava como chegou, + `_source_file` e `_ingested_at` | `<catalog>.orders.bronze_orders` (+ `bronze_stores`) |
| `notebooks/03_silver.py` | Remove duplicados; trata nulos; padroniza datas; converte valores (`"45,90"`, `R$`) para decimal; normaliza status | `<catalog>.orders.silver_orders` |
| `notebooks/04_gold.py` | Loja × dia, **só pedidos entregues**: `total_orders`, `total_revenue`, `average_ticket`, com `store_name`, `city`, `state`; comentários nas colunas | `<catalog>.orders.gold_sales_by_store` |
| `notebooks/05_validate.py` | Checagens que **bloqueiam a promoção**: sem duplicados na Silver, sem receita negativa, Gold não vazia, soma da Gold = soma dos entregues na Silver | — |

- As regras da Silver ficam em **`src/food/transforms.py`** (funções puras), com testes em **`tests/test_transforms.py`** rodando localmente sem Databricks (`pytest`).
- Um **job** (`food_orders_pipeline`) com as 5 tarefas em sequência, em **compute serverless**, definido no bundle (PRD 05 publica).

## 3. Passo a passo

| # | Passo | Mostrar |
|---|---|---|
| 1 | `transforms.py` + testes; rodar `pytest` (é o "TEST") | Terminal |
| 2 | Notebooks e job no bundle; `bundle deploy -t dev` | Workspace → Jobs |
| 3 | `bundle run food_orders_pipeline -t dev` | Jobs → Runs |
| 4 | `DESCRIBE DETAIL food_dev.orders.silver_orders` → `location` | SQL Editor |
| 5 | Abrir essa pasta no S3: `_delta_log/` e `.parquet` | **S3 → bucket lakehouse → `dev/`** |

O passo 5 é o momento da aula: *"a tabela é um arquivo no bucket da empresa; o Unity Catalog guarda só o metadado"*.

## 4. Critérios de aceite

- [ ] `pytest` verde.
- [ ] Job em DEV verde, incluindo o `05_validate`.
- [ ] As 3 tabelas em `food_dev.orders`, com a Gold só com pedidos entregues.
- [ ] `DESCRIBE DETAIL` aponta para `s3://{{PREFIXO}}-food-lakehouse-{{AWS_ACCOUNT_ID}}/dev/...`.
- [ ] Nenhum catálogo fixo no código.
