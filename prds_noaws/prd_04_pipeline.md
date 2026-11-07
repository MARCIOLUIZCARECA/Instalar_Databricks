# PRD 04 · Pipeline Raw → Bronze → Silver → Gold em DEV (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** catálogo `food_dev` e CSVs no volume `food_dev.orders.raw` (PRDs 01 e 03).

**Mensagem da aula:** *"do arquivo bruto ao dado de negócio; o Unity Catalog guarda o metadado e o dado físico fica num storage que você governa"*.

---

## 1. Objetivo

Uma única pipeline, simples, que mostra o ciclo de vida do dado. O código nasce **só em DEV**; a promoção é o PRD 05.

Fora de escopo: streaming, Auto Loader com file events, ML, múltiplas pipelines, cluster clássico.

## 2. O que construir

O catálogo **não é fixo no código**: vem por parâmetro (`catalog`, padrão `food_dev`), para o mesmo código rodar em PROD.

| Notebook | Faz | Tabela |
|---|---|---|
| `notebooks/01_ingestion.py` | Lê os CSVs do volume `/Volumes/<catalog>/orders/raw/` como texto; mostra schema e amostras | — |
| `notebooks/02_bronze.py` | Grava como chegou, + `_source_file` e `_ingested_at` | `<catalog>.orders.bronze_orders` (+ `bronze_stores`) |
| `notebooks/03_silver.py` | Remove duplicados; trata nulos; padroniza datas; converte valores (`"45,90"`, `R$`) para decimal; normaliza status | `<catalog>.orders.silver_orders` |
| `notebooks/04_gold.py` | Loja × dia, **só pedidos entregues**: `total_orders`, `total_revenue`, `average_ticket`, com `store_name`, `city`, `state`; comentários nas colunas | `<catalog>.orders.gold_sales_by_store` |
| `notebooks/05_validate.py` | Checagens que **bloqueiam a promoção**: sem duplicados na Silver, sem receita negativa, Gold não vazia, soma da Gold = soma dos entregues na Silver | — |

- As regras da Silver ficam em **`src/food/transforms.py`** (funções puras), com testes em **`tests/test_transforms.py`** rodando localmente sem Databricks (`pytest`).
- Um **job** (`food_orders_pipeline`) com as 5 tarefas em sequência, em **compute serverless** (o Express só tem serverless), definido no bundle (`databricks.yml`, target `dev` apontando para o profile `{{WS_DEV}}`; o target `prod` vem no PRD 05). Use a skill `databricks-jobs`.
- Use `_metadata.file_path` (não `input_file_name()`), que é o compatível com serverless.

## 3. Passo a passo

| # | Passo | Onde ver |
|---|---|---|
| 1 | `transforms.py` + testes; rodar `pytest` (é o "TEST") | Terminal |
| 2 | Notebooks e job no bundle; `databricks bundle deploy -t dev` | Jobs & Pipelines |
| 3 | `databricks bundle run food_orders_pipeline -t dev` | Jobs → Runs |
| 4 | `DESCRIBE DETAIL food_dev.orders.silver_orders` → mostrar `location` e `format = delta` | SQL Editor |
| 5 | `DESCRIBE HISTORY food_dev.orders.silver_orders` e a aba *Lineage* da Gold | Catalog Explorer → tabela → History / Lineage |

O passo 4 é o momento da aula. Na versão AWS, abríamos o bucket e víamos `_delta_log/` e `.parquet`. Aqui, o `location` aponta para o **storage gerenciado pela Databricks**: o princípio é o mesmo (*a tabela é um conjunto de arquivos Delta; o Unity Catalog guarda o metadado*), só que o bucket não é seu. Mostre o History e o Lineage como evidência.

## 4. Critérios de aceite

- [ ] `pytest` verde.
- [ ] Job em DEV verde, incluindo o `05_validate`, em serverless.
- [ ] As 3 tabelas em `food_dev.orders`, com a Gold só com pedidos entregues.
- [ ] Nenhum catálogo fixo no código; nenhum `s3://`.
- [ ] Nenhum arquivo, consulta ou recurso usa um catálogo automático (`{{CATALOGO_AUTOMATICO_DEV}}`, `{{CATALOGO_AUTOMATICO_PROD}}`); tudo é `food_<ambiente>` em três partes.
