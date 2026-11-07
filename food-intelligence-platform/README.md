# Food Intelligence Platform

Projeto do workshop **Do Zero à Produção — Databricks Enterprise na AWS** (PRD em [`../.llm/prd.md`](../.llm/prd.md)).

Uma empresa fictícia de delivery organiza a sua plataforma de dados no Databricks: dois ambientes (DEV e PROD; HML opcional), grupos de acesso, Unity Catalog sobre o S3, uma pipeline Bronze → Silver → Gold e três formas de consumo (Dashboard, App e Genie).

```
AWS → Databricks Account → Workspaces → Ambientes → Grupos → Unity Catalog → S3 → Pipeline → Negócio
```

Arquitetura completa: [docs/architecture.md](docs/architecture.md).

## O desafio

**Cenário do exercício:** fomos contratados pela Coca-Cola para implementar o Databricks. *(Cenário inspirado em experiência real; nenhum dado, número ou arquitetura da empresa é usado. Os dados da demo são de uma rede de delivery fictícia.)*

Antes de abrir qualquer console, o cliente pergunta:

| Pergunta do cliente | Onde respondemos |
|---|---|
| Qual plataforma: Databricks, Snowflake, Fabric ou continuar on-premise? | Abertura da aula (comparação, vantagens, desvantagens e limites) |
| Quanto custa, e quem cobra: só a Databricks, Databricks + AWS, ou tudo na fatura da AWS (Marketplace)? | Fundamentos ("Quem cobra o quê") e bloco de custos |
| Como começar sem travar a segurança: Free, Trial, Express ou setup completo? | Bloco 1 (Express) e bloco 2 (setup manual) |
| Quantos ambientes, e quanto custa cada opção? | Bloco 3 ([environments.md](docs/environments.md#quantos-ambientes)) |
| Como governar centenas de pessoas? | Bloco 4 ([governance.md](docs/governance.md)) |
| Como o dado chega ao negócio? | Blocos 5 e 6 (pipeline e consumo) |

O objetivo não é vender o Databricks, e sim mostrar **vantagens, desvantagens e limites de cada caminho**, como um arquiteto faria para o cliente.

**Material da aula:** apresentação (link no [roteiro de fala](docs/roteiro-slides.md)), [roteiro de fala slide a slide](docs/roteiro-slides.md) e [roteiro do instrutor](docs/workshop-guide.md).

## Ordem de execução

A infraestrutura nasce **completa** (DEV e PROD). O código nasce **só em DEV** e é promovido. Por que dois ambientes e quanto custa cada opção: [docs/environments.md](docs/environments.md#quantos-ambientes).

| # | Etapa | Onde | Comando / guia |
|---|---|---|---|
| 0 | Logins (conta Databricks + AWS) | terminal | [manual, seção 7](../manual/README.md#7-login-pelo-terminal-e-claude-code) |
| 1 | Workspaces FOOD-DEV e FOOD-PROD | [`../terraform`](../terraform/README.md) | `terraform apply` · [docs/workspaces.md](docs/workspaces.md) |
| 2 | Login em cada workspace | terminal | `databricks auth login --host <url> --profile food-dev` (e food-prod) |
| 3 | Buckets raw/lakehouse, grupos, usuários, catálogos, permissões | [`infrastructure/terraform`](infrastructure/terraform) | `terraform apply` · [docs/governance.md](docs/governance.md) |
| 4 | Dados sintéticos no bucket raw | [`data/`](data) | `./data/upload_to_s3.sh dev <profile-aws>` (e prod) |
| 5 | Pipeline em DEV | bundle | `databricks bundle deploy -t dev && databricks bundle run food_orders_pipeline -t dev` |
| 6 | Promoção DEV → TEST → PROD | bundle | [docs/environments.md](docs/environments.md) |
| 7 | Consumo: Dashboard, App, Genie | bundle (PROD) | [docs/consumption.md](docs/consumption.md) |
| 8 | Teste de ponta a ponta | terminal | `python3 scripts/smoke_test.py` → "TUDO OK" |

Roteiro de 4 horas do instrutor: [docs/workshop-guide.md](docs/workshop-guide.md).

**Está tudo funcionando?** `python3 scripts/smoke_test.py` confere, em DEV e PROD, workspace, catálogo, arquivos no raw, pipeline, camadas, permissões, dashboard, Genie e App (só leitura).

**Vai criar à mão?** Policies preenchidas e prontas para colar: `python3 ../manual/policies/gerar_policies.py --aws <ID> --databricks <ID>` → `manual/policies/prontas/<ID>/COLAR.md`.

**Vai montar numa conta nova?** Leia antes [docs/troubleshooting.md](docs/troubleshooting.md): o checklist com tudo que travou no ensaio (SCP/RCP, limite diário de workspaces, catálogo automático, SQL serverless) e como evitar.

## Scripts

| Script | Para quê | Como usar |
|---|---|---|
| `data/generate_orders.py` | Gera `stores.csv` e `orders.csv` sintéticos, com "sujeira" proposital para a Silver limpar | `python3 data/generate_orders.py [--orders 20000 --stores 30]` |
| `data/upload_to_s3.sh` | Envia os CSVs para o bucket raw do ambiente (`s3://food-intelligence-raw-<conta>/<env>/orders/`) | `./data/upload_to_s3.sh dev <profile-aws>` (região padrão us-east-2) |
| `tests/test_orders.py` | Testes locais das regras da Silver e do gerador (o "TEST") | `uv run --no-project --with pytest pytest tests -q` |
| `dashboards/build_dashboard.py` | Regera o JSON do AI/BI Dashboard | `python3 dashboards/build_dashboard.py` |
| `genie/build_genie_space.py` | Regera a definição do Genie para `food_dev` e `food_prod` | `python3 genie/build_genie_space.py` |
| `scripts/smoke_test.py` | Teste de ponta a ponta em DEV e PROD (só leitura): workspace, catálogo, raw, pipeline, camadas, permissões, dashboard, Genie e App | `python3 scripts/smoke_test.py [dev\|prod]` |
| `../manual/policies/gerar_policies.py` | Policies IAM/S3 preenchidas, prontas para colar no console | `python3 ../manual/policies/gerar_policies.py --aws <ID> --databricks <ID> --prefix workshop` |

Comandos do bundle (rodar nesta pasta):

```bash
databricks bundle validate -t dev
databricks bundle deploy   -t dev && databricks bundle run food_orders_pipeline -t dev
databricks bundle deploy   -t prod && databricks bundle run food_orders_pipeline -t prod
databricks bundle deploy   -t prod                     # 2ª passada: cria o Genie (precisa da Gold)
databricks bundle run food_explorer -t prod            # sobe o Data App
databricks warehouses start <id> -p food-prod          # 15 min antes da aula
```

## Estrutura

```text
food-intelligence-platform/
├── databricks.yml                 # bundle: targets dev e prod (hml opcional)
├── resources/                     # job, dashboard e app do bundle
├── notebooks/                     # 01_ingestion → 05_validate
├── src/food/transforms.py         # regras da Silver (testadas localmente)
├── tests/test_orders.py           # pytest: o estágio "TEST"
├── data/                          # gerador de dados + upload para o S3 raw
├── dashboards/                    # AI/BI Dashboard (JSON gerado por build_dashboard.py)
├── app/                           # Databricks App (Streamlit)
├── genie/                         # Genie space (JSON gerado por build_genie_space.py)
├── infrastructure/terraform/      # governança: buckets, IAM, UC, grupos, grants
├── scripts/smoke_test.py          # teste de ponta a ponta (DEV e PROD)
└── docs/
    ├── architecture.md · aws-setup.md · workspaces.md · environments.md
    ├── governance.md · consumption.md
    ├── workshop-guide.md          # roteiro do instrutor (4h)
    ├── roteiro-slides.md          # roteiro de fala slide a slide (= notas do deck)
    └── troubleshooting.md         # lições do ensaio e checklist para conta nova
```

A infraestrutura de conta (bucket raiz, roles, credential, workspaces) fica no stack que já existia, [`../terraform`](../terraform), documentado passo a passo no [`../manual`](../manual/README.md).

## Pré-requisitos locais

- Databricks CLI `>= 0.270` (`databricks version`)
- Terraform `>= 1.5`
- AWS CLI v2
- Python 3.10+ e [uv](https://docs.astral.sh/uv/) para os testes

```bash
uv run --no-project --with pytest pytest tests -q   # testes locais
python data/generate_orders.py                       # gera data/output/*.csv
```

## Custos

Os workspaces são **clássicos**: cada um tem a sua VPC, com NAT Gateway e IP público cobrados por hora (~US$ 1,20/dia por workspace, mesmo parado). Os jobs e o App usam compute **serverless** (cobrado só durante o uso). Dashboard, App e Genie consultam pelo `Food Classic Warehouse` (clássico, 2X-Small, desliga após 10 min parado), porque o SQL serverless deu 403 nos buckets da conta do ensaio ([troubleshooting.md](docs/troubleshooting.md)). Ao final, siga a limpeza em [docs/workspaces.md](docs/workspaces.md#limpeza).
