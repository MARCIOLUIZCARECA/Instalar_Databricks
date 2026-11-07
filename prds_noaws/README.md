# PRDs SEM AWS · Food Intelligence com Claude Code (Express setup)

Versão dos PRDs para quem **não tem conta AWS**. Tudo roda numa conta Databricks criada pelo **Express setup** (login.databricks.com/signup), com workspaces **serverless** e storage gerenciado pela Databricks.

**O que muda:** o Claude Code cria **dois workspaces serverless** (DEV e PROD) além do Express, sem nada na AWS; `food_dev` nasce no DEV e `food_prod` no PROD; os CSVs vão para um volume do Unity Catalog em vez do S3. Nada de bucket, role, VPC ou comando `aws`. Detalhes no [`prd_00_contexto.md`](prd_00_contexto.md), seção 2.

## Antes de começar

1. Crie a conta em login.databricks.com/signup (Express) e anote o **Account ID** (Account Console → avatar). O PRD 01 faz login de conta para criar os workspaces.
2. Instale o Databricks CLI e o Claude Code.
3. Copie esta pasta para a raiz de um projeto novo, com o nome `prds_noaws/`.

| PRD | Etapa |
|---|---|
| [`prd_00_contexto.md`](prd_00_contexto.md) | Cenário, diferenças para a versão AWS, regras (vale para todos) |
| [`prd_01_workspaces_serverless.md`](prd_01_workspaces_serverless.md) | Login de conta, `config.yaml`, workspaces serverless DEV e PROD e os catálogos `food_dev` / `food_prod` |
| [`prd_02_governanca.md`](prd_02_governanca.md) | Grupos na conta, acesso aos workspaces e permissões |
| [`prd_03_dados.md`](prd_03_dados.md) | Pedidos e lojas sintéticos no volume `raw` |
| [`prd_04_pipeline.md`](prd_04_pipeline.md) | Raw → Bronze → Silver → Gold em DEV, com testes |
| [`prd_05_promocao.md`](prd_05_promocao.md) | DEV → TEST → PROD com Asset Bundles |
| [`prd_06_consumo.md`](prd_06_consumo.md) | Dashboard, App e Genie sobre a Gold |

## Os 6 prompts (cole um por vez no Claude Code)

**1 · Workspaces serverless DEV e PROD + catálogos**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_01_workspaces_serverless.md`. Não tenho conta AWS. Me ajude a fazer login de conta no CLI, preencher o `prds_noaws/config.yaml`, criar os workspaces serverless de DEV e PROD e, em cada um, o catálogo do ambiente (`food_dev` no DEV, `food_prod` no PROD), com o schema `orders` e o volume `raw`. Vamos passo a passo, pedindo aprovação antes de criar ou alterar qualquer coisa.

**2 · Governança**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_02_governanca.md` e use os valores do `prds_noaws/config.yaml`. Os workspaces e os catálogos já existem (PRD 01). Crie os grupos e os usuários fictícios na conta, atribua cada grupo aos workspaces certos e aplique as permissões em `food_dev` e `food_prod`. Mostre cada comando antes e espere meu "pode".

**3 · Dados**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_03_dados.md`. Gere os dados sintéticos de pedidos e lojas, me mostre a sujeira proposital e envie os CSVs para os volumes `raw` de DEV e PROD.

**4 · Pipeline**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_04_pipeline.md`. Construa a pipeline Raw → Bronze → Silver → Gold em DEV, com as regras da Silver testadas por `pytest`, o job serverless no bundle e o notebook de validação. Rode em DEV e me mostre onde ficam as tabelas.

**5 · Promoção**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_05_promocao.md`. Configure o target `prod` do bundle, mostre o que muda em relação a DEV e, só depois que eu disser "pode publicar em PROD", publique e rode o job. Depois aplique os grants da Gold e me ajude a validar com dois usuários.

**6 · Consumo**
> Leia `prds_noaws/prd_00_contexto.md` e `prds_noaws/prd_06_consumo.md`. Crie o Dashboard, o App e o Genie lendo `food_prod.orders.gold_sales_by_store`, testando cada query antes do deploy, e publique na ordem do PRD.

O Claude Code pede aprovação antes de criar, alterar ou apagar qualquer coisa.
