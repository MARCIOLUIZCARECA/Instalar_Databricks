# PRD 03 · Dados sintéticos no volume raw (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** volumes `food_dev.orders.raw` e `food_prod.orders.raw` (PRD 01).

**Mensagem da aula:** *"o arquivo bruto chega ao lake da empresa, e o Databricks lê de lá"*. Na versão com AWS, o lake é um bucket S3; aqui, é um **volume** do Unity Catalog no storage gerenciado.

---

## 1. Objetivo

Gerar pedidos e lojas sintéticos, com "sujeira" proposital para a Silver limpar, e enviar para os volumes `raw` de DEV e PROD.

## 2. O que construir

**`data/generate_orders.py`** (só biblioteca padrão), com `--orders` (padrão 20000), `--stores` (padrão 30) e `--seed` (reprodutível). Gera em `data/output/`:

`stores.csv`: `store_id, store_name, city, state, region`. Lojas fictícias em cidades brasileiras.

`orders.csv`:

```text
order_id, store_id, order_date, product_name, quantity, total_amount, order_status
```

- `order_status` ∈ `delivered`, `cancelled`, `in_progress`.
- Período: os últimos ~6 meses.
- **Sujeira proposital** (cerca de 1% a 3% de cada uma):
  - `order_id` duplicado;
  - `total_amount` com vírgula decimal (`"45,90"`) ou com `R$`;
  - `order_date` em formatos diferentes (`2026-10-03`, `03/10/2026`);
  - nulos em `quantity` ou `product_name`;
  - status em maiúsculas ou com espaço.

**`data/upload_to_volume.sh <env> <profile>`**: envia os dois CSVs para `/Volumes/food_<env>/orders/raw/` com `databricks fs cp --overwrite dbfs:/Volumes/food_<env>/orders/raw/... --profile <profile>`. Valida que `<env>` é `dev` ou `prod`.

## 3. Passo a passo

| # | Passo | Onde ver |
|---|---|---|
| 1 | Gerar os CSVs e mostrar 5 linhas de cada, apontando a sujeira | Terminal |
| 2 | Enviar para `dev` e `prod` (aprovação antes) | Catalog Explorer → `food_dev.orders.raw` |
| 3 | Listar pelo SQL: `LIST '/Volumes/food_dev/orders/raw/'` e ler 5 linhas com `read_files` | SQL Editor |

**Plano B** se o CLI falhar no upload: no Catalog Explorer, abrir o volume → *Upload to this volume* e arrastar os dois CSVs.

## 4. Critérios de aceite

- [ ] `stores.csv` e `orders.csv` em `/Volumes/food_dev/orders/raw/` e `/Volumes/food_prod/orders/raw/`.
- [ ] Mesma semente = mesmos arquivos.
- [ ] Nenhum dado real. Nenhum comando `aws`.
