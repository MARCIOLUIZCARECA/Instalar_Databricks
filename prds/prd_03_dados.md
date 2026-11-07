# PRD 03 · Dados sintéticos no bucket raw

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md`.

**Pré-requisito:** bucket `{{PREFIXO}}-food-raw-{{AWS_ACCOUNT_ID}}` e volumes `raw` (PRD 02).

**Mensagem da aula:** *"o arquivo bruto chega no S3 da empresa, e o Databricks lê de lá"*.

---

## 1. Objetivo

Gerar pedidos e lojas sintéticos, com "sujeira" proposital para a Silver limpar, e enviar para as pastas de DEV e PROD do bucket raw.

## 2. O que construir

**`data/generate_orders.py`** (só biblioteca padrão), com `--orders` (padrão 20000), `--stores` (padrão 30) e `--seed` (reprodutível). Gera em `data/output/`:

`stores.csv`: `store_id, store_name, city, state, region`. Lojas fictícias em cidades brasileiras.

`orders.csv`:

```text
order_id, store_id, order_date, product_name, quantity, total_amount, order_status
```

- `order_status` ∈ `delivered`, `cancelled`, `in_progress`.
- Período: os últimos ~6 meses.
- **Sujeira proposital** (cerca de 1% a 3% de cada uma), para a Silver ter o que fazer:
  - `order_id` duplicado;
  - `total_amount` com vírgula decimal (`"45,90"`) ou com `R$`;
  - `order_date` em formatos diferentes (`2026-10-03`, `03/10/2026`);
  - nulos em `quantity` ou `product_name`;
  - status em maiúsculas ou com espaço.

**`data/upload_to_s3.sh <env> <profile-aws>`**: envia os dois CSVs para `s3://{{PREFIXO}}-food-raw-{{AWS_ACCOUNT_ID}}/<env>/orders/`, com região `{{REGIAO}}` explícita.

## 3. Passo a passo

| # | Passo | Mostrar no console |
|---|---|---|
| 1 | Gerar os CSVs e mostrar 5 linhas de cada, apontando a sujeira | Terminal |
| 2 | Enviar para `dev` e `prod` (aprovação antes) | S3 → bucket raw → `dev/orders/` |
| 3 | Listar os arquivos pelo volume, no workspace | Catalog Explorer → `food_dev.orders.raw` |

## 4. Critérios de aceite

- [ ] `stores.csv` e `orders.csv` em `raw/dev/orders/` e `raw/prod/orders/`.
- [ ] Os arquivos aparecem no volume `raw` dos dois catálogos.
- [ ] Mesma semente = mesmos arquivos.
- [ ] Nenhum dado real.
