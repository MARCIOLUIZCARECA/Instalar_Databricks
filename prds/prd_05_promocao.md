# PRD 05 · Promoção DEV → TEST → PROD com Asset Bundles

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md`.

**Pré-requisito:** pipeline verde em DEV (PRD 04).

**Mensagem da aula:** *"nada se desenvolve direto em produção: o mesmo código, validado, vai para PROD"*.

---

## 1. Objetivo

Publicar em PROD **a mesma versão** que passou em DEV, mudando só a configuração por ambiente.

```text
DEV (desenvolve) → TEST (pytest + 05_validate) → PROD (publica, com aprovação)
```

TEST é uma etapa automatizada, não um workspace. HML fica documentado como opcional.

## 2. O que construir

**`databricks.yml`** com dois targets:

| Target | Workspace | `catalog` | Modo |
|---|---|---|---|
| `dev` | `{{WS_DEV}}` (profile `{{WS_DEV}}`) | `food_dev` | `development` (prefixo `[dev <usuário>]`) |
| `prod` | `{{WS_PROD}}` (profile `{{WS_PROD}}`) | `food_prod` | `production`: pasta `/Workspace/Projects/...`, permissões de *Can view* para `data-engineering`, `CAN_MANAGE` para `platform-admins` |

Use a nomenclatura atual (Declarative Automation Bundles / Asset Bundles) e a skill `databricks-dabs`.

Um exemplo **documentado, sem executar** de GitHub Actions com service principal: `pytest` → `bundle deploy -t prod`.

## 3. Passo a passo

| # | Passo | Mostrar |
|---|---|---|
| 1 | `pytest` | Terminal |
| 2 | `bundle run food_orders_pipeline -t dev`: `05_validate` verde = pode promover | Jobs (DEV) |
| 3 | `bundle validate -t prod` e mostrar o que muda (catálogo, pasta, permissões) | Terminal |
| 4 | **Confirmação explícita do instrutor** → `bundle deploy -t prod` | — |
| 5 | `bundle run food_orders_pipeline -t prod` | Jobs (PROD): sem prefixo `[dev ...]` |
| 6 | Grants da Gold de PROD para marketing, operações e diretoria (PRD 02) e validação com dois perfis | Catalog Explorer; janelas anônimas |

## 4. Critérios de aceite

- [ ] Mesmo commit publicado em DEV e PROD.
- [ ] Job de PROD verde; `food_prod.orders.gold_sales_by_store` preenchida.
- [ ] Engenharia só com *Can view* no job de PROD.
- [ ] Marketing lê a Gold de PROD e recebe `PERMISSION_DENIED` na Silver.
- [ ] Exemplo de CI/CD documentado.
