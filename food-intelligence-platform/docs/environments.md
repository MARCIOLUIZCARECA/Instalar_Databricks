# Ambientes e promoção (DEV → TEST → PROD)

**Regra:** nada é desenvolvido direto em produção. O mesmo código passa por desenvolvimento, teste e aprovação.

```text
DEV   desenvolver no FOOD-DEV, catálogo food_dev          databricks bundle deploy -t dev
 │
TEST  testes automáticos: pytest local + 05_validate       pytest tests  /  task "validate" do job
 │    (+ aprovação: pull request revisado)
PROD  publicar no FOOD-PROD                                databricks bundle deploy -t prod
```

TEST é uma **etapa**, não um workspace.

## Quantos ambientes?

Escolha de arquitetura **e** de custo. Não há resposta certa: é troca entre risco, velocidade e dinheiro.

| Opção | Workspaces | Vantagens | Desvantagens | Para quem |
|---|---|---|---|---|
| Só PROD | 1 | Mais barato e simples | Testa em produção; um erro chega no negócio | Prova de conceito, time de 1 a 3 pessoas |
| **DEV + PROD** (este projeto) | 2 | Produção isolada; custo moderado; promoção simples | Validação final acontece em DEV, com dados de DEV | A maioria dos times |
| DEV + HML + PROD | 3 | Homologação com dados e acessos parecidos com produção; aprovação formal | Mais caro; entrega mais lenta; mais coisa para manter | Empresas reguladas, muitos times |

**Custo fixo por workspace clássico** (preço público AWS us-east-2, sob demanda; confira na calculadora da AWS):

| | Por hora | Por dia | Por mês (730 h) |
|---|---|---|---|
| NAT Gateway | US$ 0,045 | US$ 1,08 | US$ 32,85 |
| IPv4 público do NAT | US$ 0,005 | US$ 0,12 | US$ 3,65 |
| **Total por workspace** | **US$ 0,05** | **US$ 1,20** | **≈ US$ 36,50** |

| Opção | Custo fixo/mês |
|---|---|
| Só PROD | ≈ US$ 36 |
| DEV + PROD | ≈ US$ 73 |
| DEV + HML + PROD | ≈ US$ 110 |

Fora desse fixo: tráfego no NAT (US$ 0,045/GB), EC2 dos clusters clássicos, DBUs (jobs, SQL, serverless) e S3. Esses crescem com o **uso**, não com o número de ambientes.

O TEST automático (pytest + task `validate`) cobre boa parte do papel do HML sem custar um workspace.

### Ligar o HML depois

O código já aceita o terceiro ambiente, só com configuração:

1. `terraform/terraform.tfvars`: `environments = { dev = "FOOD-DEV", hml = "FOOD-HML", prod = "FOOD-PROD" }` e `terraform apply`.
2. `databricks auth login --host <url-hml> --profile food-hml`.
3. `infrastructure/terraform/terraform.tfvars`: incluir `hml = <id>` em `workspace_ids` e `terraform apply` (cria `food_hml` e os acessos de validação).
4. `databricks bundle deploy -t hml` (o target já existe em `databricks.yml`).

> A conta Databricks tem **limite diário de criação de workspaces**. Planeje com antecedência.

## O que muda entre ambientes

Só configuração. O código (notebooks, `src/`) é idêntico. Tudo está em [`../databricks.yml`](../databricks.yml):

| | dev | prod |
|---|---|---|
| Workspace (profile) | `food-dev` | `food-prod` |
| `mode` | development | production |
| Catálogo | `food_dev` | `food_prod` |
| Pasta do código | `/Workspace/Users/<você>/.bundle/...` | `/Workspace/Projects/food-intelligence/prod` |
| Nome do job | `[dev <você>] food-orders-pipeline-dev` | `food-orders-pipeline-prod` |
| SELECT na Gold para o negócio | não | marketing, operações, diretoria |
| Genie | sim (teste) | sim |
| Agendamento | pausado | pausado (ligue após aprovar) |

`mode: development` prefixa os recursos com o nome de quem publicou e pausa agendamentos, para cada pessoa ter a sua cópia sem pisar na dos outros.

## Passo a passo

```bash
cd food-intelligence-platform

# DEV
uv run --no-project --with pytest pytest tests -q
databricks bundle validate -t dev
databricks bundle deploy   -t dev
databricks bundle run food_orders_pipeline -t dev

# PROD (após TEST verde e aprovação)
databricks bundle deploy -t prod
databricks bundle run food_orders_pipeline -t prod
databricks bundle run food_explorer -t prod           # inicia o App
```

## Exemplo de CI/CD (documentado, não executado no workshop)

`.github/workflows/deploy.yml` (sugestão):

```yaml
name: deploy
on:
  pull_request:            # TEST + DEV a cada PR
  workflow_dispatch:       # PROD manual, com aprovação do environment "prod"
    inputs:
      target: { default: prod }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv run --no-project --with pytest pytest food-intelligence-platform/tests -q

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: ${{ github.event_name == 'workflow_dispatch' && 'prod' || 'dev' }}
    defaults: { run: { working-directory: food-intelligence-platform } }
    env:
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ vars.DATABRICKS_CLIENT_ID }}          # service principal
      DATABRICKS_CLIENT_SECRET: ${{ secrets.DATABRICKS_CLIENT_SECRET }}
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy -t ${{ github.event_name == 'workflow_dispatch' && 'prod' || 'dev' }}
```

Em uma empresa, PROD (e HML, se existir) é publicado por um **service principal** (não por uma pessoa), e o environment `prod` do GitHub exige aprovação manual.
