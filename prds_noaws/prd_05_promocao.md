# PRD 05 · Promoção DEV → TEST → PROD com Asset Bundles (sem AWS)

**Para quem lê:** o Claude Code. Leia antes o `prd_00_contexto.md` desta pasta.

**Pré-requisito:** pipeline verde em DEV (PRD 04).

**Mensagem da aula:** *"nada se desenvolve direto em produção: o mesmo código, validado, vai para PROD"*.

---

## 1. Objetivo

Publicar em PROD **a mesma versão** que passou em DEV, mudando só a configuração por ambiente.

```text
DEV (desenvolve) → TEST (pytest + 05_validate) → PROD (publica, com aprovação)
```

TEST é uma etapa automatizada, não um ambiente. Nesta versão, DEV e PROD estão **no mesmo workspace** `{{WS}}`; o que os separa é o **catálogo**, a **pasta** e as **permissões**. Explique que, numa empresa, PROD seria outro workspace (versão AWS), e que o bundle muda só uma linha (`workspace.host`) para isso.

## 2. O que construir

**`databricks.yml`** com dois targets, ambos com `workspace.profile: {{WS}}`:

| Target | `catalog` | Modo | Pasta |
|---|---|---|---|
| `dev` | `food_dev` | `development` (prefixo `[dev <usuário>]`, schedules pausados) | padrão do usuário |
| `prod` | `food_prod` (nunca o automático) | `production` | `/Workspace/Projects/food-intelligence` (`root_path`), *Can view* para `data-engineering`, `CAN_MANAGE` para `platform-admins` |

No target `prod`, defina `run_as` como o próprio aluno (`{{USUARIO}}`) — service principal é opcional e pode não estar disponível no Express; se estiver, mostre como seria.

Use a nomenclatura atual (Declarative Automation Bundles / Asset Bundles) e a skill `databricks-dabs`.

Um exemplo **documentado, sem executar** de GitHub Actions com service principal: `pytest` → `bundle deploy -t prod`.

## 3. Passo a passo

| # | Passo | Onde ver |
|---|---|---|
| 1 | `pytest` | Terminal |
| 2 | `bundle run food_orders_pipeline -t dev`: `05_validate` verde = pode promover | Jobs (`[dev ...]`) |
| 3 | `bundle validate -t prod` e mostrar o que muda (catálogo, pasta, permissões, nome sem prefixo) | Terminal |
| 4 | **Confirmação explícita do aluno/instrutor** → `bundle deploy -t prod` | — |
| 5 | `bundle run food_orders_pipeline -t prod` | Jobs: agora há **dois** jobs, o `[dev ...]` e o de PROD |
| 6 | Grants da Gold de PROD (`SELECT` em `food_prod.orders.gold_sales_by_store`) para marketing, operações e diretoria; validação com dois perfis (PRD 02, seção 7) | Catalog Explorer → Permissions; janelas anônimas |

## 4. Critérios de aceite

- [ ] Mesmo commit publicado em `dev` e `prod`.
- [ ] Job de PROD verde; `food_prod.orders.gold_sales_by_store` preenchida.
- [ ] Engenharia só com *Can view* no job de PROD.
- [ ] Marketing lê a Gold de PROD e recebe `PERMISSION_DENIED` na Silver e em `food_dev`.
- [ ] Exemplo de CI/CD documentado.
- [ ] Nenhum arquivo, consulta ou recurso usa o catálogo automático; tudo é `food_<ambiente>` em três partes.
